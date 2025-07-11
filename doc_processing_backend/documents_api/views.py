import asyncio
import threading
import traceback
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

# Import models
from .models import (
    Document, Workflow, WorkflowStep, ValidationRule, Notification,
    IntegrationConfiguration, IntegrationAuditLog, DocumentApproval,
    WorkflowExecution, RealTimeSyncStatus
)

# Import serializers
from .serializers import (
    DocumentSerializer, WorkflowSerializer, WorkflowStepSerializer, 
    ValidationRuleSerializer, NotificationSerializer, UserSerializer,
    IntegrationConfigurationSerializer, IntegrationAuditLogSerializer,
    DocumentApprovalSerializer, WorkflowExecutionSerializer,
    RealTimeSyncStatusSerializer, DocumentWithApprovalsSerializer,
    WorkflowWithExecutionsSerializer
)

from django.http import Http404, HttpResponse
import io
import csv
import json
import uuid

# Import the AI services
from .services.classification_service import classify_document, detect_document_language
from langdetect.detector import LangDetectException
from .services.extraction_service import extract_data, extract_data_from_document, convert_to_format, validate_and_clean_data
from .services.nlp_service import summarize_document, semantic_document_understanding
from .services.workflow_service import (
    process_document_in_workflow, 
    create_workflow, 
    get_workflow_templates,
    send_workflow_notification,
    start_document_workflow,
    send_email_notification,
    workflow_service
)
from .services.integration_service import (
    send_to_external_system, 
    get_available_integrations,
    integration_service,
    sync_service
)
from .services.llm_service import process_document_with_llm
from .services.validation_service import validate_document_data
from .services.pattern_analysis_service import analyze_document_patterns, auto_create_validation_rules
from asgiref.sync import sync_to_async

def run_pipeline_in_background(document_id):
    """
    Wrapper function to run the async pipeline in a new thread.
    This prevents blocking the main server thread.
    """
    asyncio.run(process_document_pipeline(document_id))

async def process_document_pipeline(document_id):
    """
    The main asynchronous AI processing pipeline.
    """
    try:
        document = await Document.objects.aget(id=document_id)
        print(f"Starting AI pipeline for {document.filename}...")

        # --- STEP 1: Extract text from document using OCR ---
        extracted_text = await extract_data_from_document(document.uploaded_file.path)
        if not extracted_text:
            raise Exception("Failed to extract text from document.")

        print(f"Successfully extracted text from {document.filename}")

        # --- STEP 2: Detect document language ---
        from .services.language_service import detect_and_get_language_name
        detected_language_name = detect_and_get_language_name(extracted_text)
        document.detected_language = detected_language_name
        print(f"Detected language: {detected_language_name}")

        # --- STEP 3: Process with LLM for comprehensive analysis ---
        try:
            # Process document with LLM to get document type, extracted data, and summary
            llm_results = await process_document_with_llm(extracted_text)
            
            # Validate and clean the extracted data
            llm_results = validate_and_clean_data(llm_results)
            
            # Update document with results from LLM
            document.document_type = llm_results.get('document_type', 'Unknown')
            document.extracted_data = llm_results.get('extracted_data', {})
            document.summary = llm_results.get('summary', '')
            document.sentiment = llm_results.get('sentiment', 'Neutral')
            
            # Add raw text to extracted data for reference
            if document.extracted_data is None:
                document.extracted_data = {}
            document.extracted_data['raw_text'] = {
                "value": extracted_text,
                "confidence": "High"
            }
            
            print(f"Successfully processed document with LLM: classified as {document.document_type}")
            
            # --- STEP 4: Validate extracted data against validation rules ---
            print(f"Starting validation for document type: {document.document_type}")
            try:
                validation_results = await validate_document_data(document.extracted_data, document.document_type)
                
                # Store validation results in the document
                document.extracted_data['validation_results'] = validation_results
                
                # Log validation results
                if validation_results['status'] == 'passed':
                    print(f"✅ Validation PASSED: {validation_results['passed_rules']}/{validation_results['total_rules']} rules passed")
                elif validation_results['status'] == 'failed':
                    print(f"❌ Validation FAILED: {validation_results['failed_rules']}/{validation_results['total_rules']} rules failed")
                    for error in validation_results['errors']:
                        print(f"   - {error}")
                elif validation_results['status'] == 'no_rules':
                    print(f"⚠️ No validation rules found for document type: {document.document_type}")
                
                # Add validation summary to document summary
                validation_summary = f"\n\nValidation Results:\n"
                validation_summary += f"Status: {validation_results['status'].upper()}\n"
                validation_summary += f"Rules Applied: {validation_results['total_rules']}\n"
                validation_summary += f"Passed: {validation_results['passed_rules']}\n"
                validation_summary += f"Failed: {validation_results['failed_rules']}\n"
                
                if validation_results['errors']:
                    validation_summary += f"Errors:\n"
                    for error in validation_results['errors'][:3]:  # Show first 3 errors
                        validation_summary += f"- {error}\n"
                    if len(validation_results['errors']) > 3:
                        validation_summary += f"... and {len(validation_results['errors']) - 3} more errors\n"
                
                document.summary += validation_summary
                
            except Exception as e:
                print(f"⚠️ Validation step failed: {str(e)}")
                # Add validation error to extracted data but don't fail the pipeline
                if document.extracted_data is None:
                    document.extracted_data = {}
                document.extracted_data['validation_results'] = {
                    'status': 'error',
                    'error': f"Validation failed: {str(e)}",
                    'total_rules': 0,
                    'passed_rules': 0,
                    'failed_rules': 0,
                    'errors': [f"Validation engine error: {str(e)}"],
                    'warnings': [],
                    'field_validations': {}
                }
                document.summary += f"\n\nValidation Error: {str(e)}"
        except Exception as e:
            # If LLM processing fails, log the error and mark document as error
            print(f"LLM processing failed: {str(e)}.")
            document.status = "error"
            document.document_type = "Unknown"
            document.extracted_data = {
                "error": {
                    "value": f"Processing failed: {str(e)}",
                    "confidence": "Low"
                }, 
                "raw_text": {
                    "value": extracted_text,
                    "confidence": "High"
                }
            }
            document.summary = "Document processing failed due to an error with the LLM service."
            await document.asave()
            return

        # --- FINAL STEP ---
        document.status = "processed"
        await document.asave()
        print(f"Successfully processed and saved document: {document.filename}, type: {document.document_type}")

        # --- AUTOMATIC PATTERN ANALYSIS ---
        # Automatically learn from each document to improve validation rules
        try:
            print(f"🔍 Starting automatic pattern analysis for {document.document_type} document...")
            await auto_pattern_analysis(document.document_type, document.id)
        except Exception as e:
            print(f"⚠️ Automatic pattern analysis failed (non-critical): {str(e)}")
            # Don't fail the pipeline if pattern analysis fails

    except Document.DoesNotExist:
        print(f"Error in pipeline: Document with id {document_id} not found.")
    except Exception as e:
        traceback.print_exc()
        print(f"CRITICAL ERROR in processing pipeline for document {document_id}: {e}")
        try:
            document_to_fail = await Document.objects.aget(id=document_id)
            document_to_fail.status = "error"
            document_to_fail.summary = f"Processing failed: {str(e)}"
            await document_to_fail.asave()
        except Document.DoesNotExist:
            pass

async def auto_pattern_analysis(document_type: str, current_document_id: int):
    """
    Automatically analyze patterns and create validation rules after document processing.
    This makes the system intelligent by learning from each document.
    """
    try:
        # Count total documents of this type
        @sync_to_async
        def count_documents():
            return Document.objects.filter(
                document_type=document_type,
                status='processed'
            ).count()
        
        @sync_to_async
        def count_existing_rules():
            return ValidationRule.objects.filter(
                document_type=document_type,
                is_active=True
            ).count()
        
        doc_count = await count_documents()
        existing_rules = await count_existing_rules()
        
        print(f"📊 Found {doc_count} processed {document_type} documents, {existing_rules} existing rules")
        
        # Smart triggers for pattern analysis
        should_analyze = False
        analysis_reason = ""
        
        if existing_rules == 0 and doc_count >= 1:
            # First document of this type - analyze immediately
            should_analyze = True
            analysis_reason = "First document of this type"
        elif doc_count in [3, 5, 10, 20, 50]:
            # Key milestones - analyze to improve rules
            should_analyze = True
            analysis_reason = f"Milestone reached: {doc_count} documents"
        elif doc_count % 25 == 0:
            # Every 25 documents - continuous learning
            should_analyze = True
            analysis_reason = f"Continuous learning: {doc_count} documents"
        
        if should_analyze:
            print(f"🎯 Triggering pattern analysis: {analysis_reason}")
            
            # Run pattern analysis with smart parameters
            min_samples = max(1, min(doc_count, 5))  # At least 1, max 5
            analysis_results = await analyze_document_patterns(document_type, min_samples)
            
            if analysis_results and analysis_results.get('patterns'):
                print(f"✅ Pattern analysis completed: {len(analysis_results['patterns'])} patterns found")
                
                # Auto-create rules with confidence threshold
                confidence_threshold = 0.7 if doc_count < 5 else 0.8  # Lower threshold for early learning
                creation_results = await auto_create_validation_rules(document_type, confidence_threshold)
                
                if creation_results and creation_results.get('created_rules'):
                    created_count = len(creation_results['created_rules'])
                    print(f"🚀 Auto-created {created_count} validation rules for {document_type}")
                else:
                    print(f"📝 No new rules created (confidence threshold: {confidence_threshold})")
            else:
                print(f"📊 Pattern analysis completed but no clear patterns found yet")
        else:
            print(f"⏳ Pattern analysis skipped (will analyze at next milestone)")
            
    except Exception as e:
        print(f"❌ Error in automatic pattern analysis: {str(e)}")
        # Don't propagate error - this should not fail document processing

class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows documents to be viewed or edited.
    """
    queryset = Document.objects.all().order_by('-uploaded_at')
    serializer_class = DocumentSerializer

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Custom action to handle file uploads.
        It immediately returns a response and starts the AI processing in the background.
        """
        # Check if file was uploaded
        if 'uploaded_file' not in request.FILES:
            return Response({'error': 'No file was uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        # Extract the filename from the uploaded file
        uploaded_file = request.FILES['uploaded_file']
        filename = uploaded_file.name

        # We pass the request data to the serializer.
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Use .save() and automatically set the filename from the uploaded file
        document = serializer.save(filename=filename)
        
        # Start the AI processing in a separate background thread.
        # This allows us to return a response to the user immediately.
        thread = threading.Thread(target=run_pipeline_in_background, args=(document.id,))
        thread.start()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    
    @action(detail=True, methods=['get'], url_path='test_action')
    def test_action(self, request, pk=None):
        """
        Simple test action to verify router is working
        """
        return Response({'message': f'Test action working for document {pk}'})
    
    @action(detail=True, methods=['get'])
    def semantic_analysis(self, request, pk=None):
        """
        Perform advanced semantic analysis on the document
        """
        document = self.get_object()
        
        # Ensure document is processed
        if document.status != 'processed':
            return Response(
                {'error': 'Document has not been fully processed yet'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Start semantic analysis in a background thread and return immediately
        def run_semantic_analysis():
            asyncio.run(self._perform_semantic_analysis(document.id))
            
        thread = threading.Thread(target=run_semantic_analysis)
        thread.start()
        
        return Response({
            'status': 'processing',
            'message': 'Semantic analysis started. Results will be available soon.'
        })
    
    async def _perform_semantic_analysis(self, document_id):
        """
        Background task to perform semantic analysis
        """
        try:
            document = await Document.objects.aget(id=document_id)
            
            # Perform the semantic analysis
            semantic_results = await semantic_document_understanding(document.uploaded_file.path)
            
            # Update the document with the results
            if document.extracted_data:
                document.extracted_data['semantic_analysis'] = semantic_results
            else:
                document.extracted_data = {'semantic_analysis': semantic_results}
                
            await document.asave()
            
        except Exception as e:
            print(f"Error during semantic analysis: {e}")
            
    @action(detail=True, methods=['post'])
    def process_workflow(self, request, pk=None):
        """
        Process the document through a specified workflow
        """
        document = self.get_object()
        workflow_id = request.data.get('workflow_id')
        
        if not workflow_id:
            return Response(
                {'error': 'No workflow_id provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Start workflow processing in background thread
        def run_workflow_processing():
            asyncio.run(self._process_document_workflow(document.id, workflow_id))
            
        thread = threading.Thread(target=run_workflow_processing)
        thread.start()
        
        return Response({
            'status': 'processing',
            'message': 'Document workflow processing started.',
            'document_id': str(document.id),
            'workflow_id': workflow_id
        })
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """
        Manually trigger validation for a specific document
        """
        document = self.get_object()
        
        # Ensure document has extracted data
        if not document.extracted_data or not document.document_type:
            return Response(
                {'error': 'Document must be processed and have extracted data before validation'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Run validation in background thread since this is not an async view
            def run_validation():
                return asyncio.run(validate_document_data(document.extracted_data, document.document_type))
            
            validation_results = run_validation()
            
            # Update document with new validation results
            if document.extracted_data is None:
                document.extracted_data = {}
            document.extracted_data['validation_results'] = validation_results
            document.save()
            
            return Response({
                'status': 'completed',
                'message': 'Document validation completed',
                'validation_results': validation_results
            })
            
        except Exception as e:
            return Response(
                {'error': f'Validation failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def validation_status(self, request, pk=None):
        """
        Get detailed validation status for a document
        """
        document = self.get_object()
        
        if not document.extracted_data or 'validation_results' not in document.extracted_data:
            return Response(
                {'error': 'No validation results found for this document'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        validation_results = document.extracted_data['validation_results']
        
        return Response({
            'document_id': str(document.id),
            'document_type': document.document_type,
            'validation_results': validation_results
        })
        
    async def _process_document_workflow(self, document_id, workflow_id):
        """
        Background task to process document through workflow
        """
        try:
            result = await process_document_in_workflow(document_id, workflow_id)
            
            # Update document with workflow result
            document = await Document.objects.aget(id=document_id)
            
            if document.extracted_data:
                document.extracted_data['workflow_result'] = result
            else:
                document.extracted_data = {'workflow_result': result}
                
            # If workflow completed successfully, update document status
            if result.get('status') == 'completed':
                document.status = 'processed'
            elif result.get('status') == 'failed':
                document.status = 'error'
                
            await document.asave()
            
            # Send notification about workflow completion if needed
            await send_workflow_notification(
                'user@example.com',  # This would be the actual user email in production
                f"Workflow {result.get('workflow_name')} completed",
                f"Your document {document.filename} has been processed with status: {result.get('status')}",
                document_id=document_id,
                workflow_id=workflow_id
            )
            
        except Exception as e:
            print(f"Error during workflow processing: {e}")

    @action(detail=True, methods=['post'])
    def trigger_workflow(self, request, pk=None):
        """
        Trigger a workflow for a document.
        This starts the automation process by calling the workflow service.
        """
        document = self.get_object()
        workflow_id = request.data.get('workflow_id')
        
        if not workflow_id:
            return Response(
                {'error': 'No workflow_id provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Start the workflow in a background thread
        def run_workflow():
            asyncio.run(process_document_in_workflow(document.id, workflow_id))
            
        thread = threading.Thread(target=run_workflow)
        thread.start()
        
        return Response({
            'status': 'started',
            'message': 'Workflow automation process started',
            'document_id': str(document.id),
            'workflow_id': workflow_id
        })

    @action(detail=True, methods=['post'])
    def integrate_with_system(self, request, pk=None):
        """
        Send document data to an external system like SAP, Salesforce, etc.
        """
        document = self.get_object()
        system_name = request.data.get('system_name')
        
        if not system_name:
            return Response(
                {'error': 'No system_name provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Ensure document is processed
        if document.status != 'processed':
            return Response(
                {'error': 'Document must be fully processed before integration'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Start integration in background thread
        def run_integration():
            asyncio.run(self._integrate_document(document.id, system_name))
            
        thread = threading.Thread(target=run_integration)
        thread.start()
        
        return Response({
            'status': 'processing',
            'message': f'Integration with {system_name} started',
            'document_id': str(document.id),
            'system': system_name
        })
        
    async def _integrate_document(self, document_id, system_name):
        """
        Background task to integrate document with external system
        """
        try:
            document = await Document.objects.aget(id=document_id)
            
            # Send to external system
            result = await send_to_external_system(document, system_name)
            
            # Update document with integration result
            if document.extracted_data:
                if 'integrations' not in document.extracted_data:
                    document.extracted_data['integrations'] = []
                document.extracted_data['integrations'].append(result)
            else:
                document.extracted_data = {'integrations': [result]}
                
            await document.asave()
            
            # Send notification about integration status
            await send_workflow_notification(
                'user@example.com',  # This would be the actual user email in production
                f"Integration with {system_name} completed",
                f"Your document {document.filename} has been sent to {system_name} with status: {result.get('status')}",
                document_id=document_id
            )
            
        except Exception as e:
            print(f"Error during integration with {system_name}: {e}")
            
    @action(detail=False, methods=['get'])
    def available_integrations(self, request):
        """
        Get list of available external systems for integration
        """
        def get_integrations():
            return asyncio.run(get_available_integrations())
            
        integrations = get_integrations()
        return Response(integrations)

class WorkflowViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing document processing workflows
    """
    queryset = Workflow.objects.all().order_by('-created_at')
    serializer_class = WorkflowSerializer
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """
        Get predefined workflow templates
        """
        def get_templates():
            return asyncio.run(get_workflow_templates())
            
        templates = get_templates()
        return Response(templates)
    
    @action(detail=False, methods=['post'])
    def create_from_template(self, request):
        """
        Create a new workflow from a template
        """
        template_name = request.data.get('template_name')
        if not template_name:
            return Response(
                {'error': 'No template name provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get all templates
        def get_templates():
            return asyncio.run(get_workflow_templates())
            
        templates = get_templates()
        
        # Find the requested template
        template = None
        for t in templates:
            if t['name'] == template_name:
                template = t
                break
                
        if not template:
            return Response(
                {'error': f'Template "{template_name}" not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Create workflow from template
        def create_from_template(template):
            return asyncio.run(create_workflow(
                template['name'],
                template['description'],
                template['steps']
            ))
            
        workflow = create_from_template(template)
        
        # Return the created workflow
        serializer = self.get_serializer(workflow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class WorkflowStepViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing workflow steps
    """
    queryset = WorkflowStep.objects.all()
    serializer_class = WorkflowStepSerializer
    
    def get_queryset(self):
        """
        Optionally filter by workflow
        """
        queryset = WorkflowStep.objects.all().order_by('step_order')
        workflow_id = self.request.query_params.get('workflow_id', None)
        if workflow_id:
            queryset = queryset.filter(workflow_id=workflow_id)
        return queryset

class ValidationRuleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing validation rules.
    Users can create, view, update, and delete custom validation rules
    for different document types and fields.
    """
    queryset = ValidationRule.objects.all().order_by('-created_at')
    serializer_class = ValidationRuleSerializer
    
    def get_queryset(self):
        """
        Optionally filter by document_type.
        """
        queryset = ValidationRule.objects.all().order_by('-created_at')
        document_type = self.request.query_params.get('document_type', None)
        field_name = self.request.query_params.get('field_name', None)
        rule_type = self.request.query_params.get('rule_type', None)
        
        if document_type is not None:
            queryset = queryset.filter(document_type=document_type)
        if field_name is not None:
            queryset = queryset.filter(field_name=field_name)
        if rule_type is not None:
            queryset = queryset.filter(rule_type=rule_type)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def rule_types(self, request):
        """
        Get available rule types
        """
        rule_types = ValidationRule.RULE_TYPE_CHOICES
        return Response([{'value': rt[0], 'label': rt[1]} for rt in rule_types])
    
    @action(detail=False, methods=['get'])
    def by_document_type(self, request):
        """
        Group validation rules by document type
        """
        # Get unique document types
        document_types = ValidationRule.objects.values_list('document_type', flat=True).distinct()
        
        # Group rules by document type
        result = {}
        for doc_type in document_types:
            rules = ValidationRule.objects.filter(document_type=doc_type)
            serializer = self.get_serializer(rules, many=True)
            result[doc_type] = serializer.data
            
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def analyze_patterns(self, request):
        """
        Analyze document patterns and suggest validation rules
        """
        document_type = request.data.get('document_type')
        min_samples = request.data.get('min_samples', 5)
        
        if not document_type:
            return Response(
                {'error': 'document_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Run pattern analysis in background thread since this is not an async view
            def run_analysis():
                return asyncio.run(analyze_document_patterns(document_type, min_samples))
            
            analysis_results = run_analysis()
            
            return Response({
                'status': 'completed',
                'message': 'Pattern analysis completed',
                'results': analysis_results
            })
            
        except Exception as e:
            return Response(
                {'error': f'Pattern analysis failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def auto_create_rules(self, request):
        """
        Automatically create validation rules based on document patterns
        """
        document_type = request.data.get('document_type')
        confidence_threshold = request.data.get('confidence_threshold', 0.9)
        
        if not document_type:
            return Response(
                {'error': 'document_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Run auto-creation in background thread since this is not an async view
            def run_auto_creation():
                return asyncio.run(auto_create_validation_rules(document_type, confidence_threshold))
            
            creation_results = run_auto_creation()
            
            return Response({
                'status': 'completed',
                'message': 'Auto-creation of validation rules completed',
                'results': creation_results
            })
            
        except Exception as e:
            return Response(
                {'error': f'Auto-creation failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def test_cross_reference(self, request):
        """
        Test cross-reference validation without creating a rule
        """
        field_name = request.data.get('field_name')
        reference_field = request.data.get('reference_field')
        calculation_type = request.data.get('calculation_type', 'sum')
        tolerance = request.data.get('tolerance', 0.01)
        sample_data = request.data.get('sample_data', {})
        
        if not all([field_name, reference_field, sample_data]):
            return Response(
                {'error': 'field_name, reference_field, and sample_data are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from .services.validation_service import ValidationEngine
            
            # Create a temporary validation rule for testing
            class TempRule:
                def __init__(self):
                    self.name = 'temp_cross_reference_test'
                    self.field_name = field_name
                    self.reference_field = reference_field
                    self.calculation_type = calculation_type
                    self.tolerance = tolerance
            
            temp_rule = TempRule()
            
            # Test the cross-reference validation
            engine = ValidationEngine()
            engine.current_extracted_data = sample_data
            
            field_value = engine._get_field_value(sample_data, field_name)
            is_valid, error_message = engine._validate_cross_reference(field_value, '', temp_rule)
            
            return Response({
                'status': 'completed',
                'message': 'Cross-reference validation test completed',
                'results': {
                    'is_valid': is_valid,
                    'error_message': error_message,
                    'field_value': field_value,
                    'test_parameters': {
                        'field_name': field_name,
                        'reference_field': reference_field,
                        'calculation_type': calculation_type,
                        'tolerance': tolerance
                    }
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Cross-reference validation test failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing workflow notifications
    """
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        """
        Optionally filter by sent_status or recipient_email
        """
        queryset = Notification.objects.all().order_by('-created_at')
        sent_status = self.request.query_params.get('sent_status', None)
        recipient = self.request.query_params.get('recipient_email', None)
        document_id = self.request.query_params.get('document_id', None)
        workflow_id = self.request.query_params.get('workflow_id', None)
        
        if sent_status is not None:
            queryset = queryset.filter(sent_status=sent_status)
        if recipient is not None:
            queryset = queryset.filter(recipient_email=recipient)
        if document_id is not None:
            queryset = queryset.filter(document__id=document_id)
        if workflow_id is not None:
            queryset = queryset.filter(workflow__id=workflow_id)
            
        return queryset
        
    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """
        Resend a notification
        """
        notification = self.get_object()
        
        # Don't resend already sent notifications
        if notification.sent_status == 'sent':
            return Response(
                {'error': 'Notification has already been sent'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Start resend in background thread
        def run_resend():
            asyncio.run(send_email_notification(notification))
            
        thread = threading.Thread(target=run_resend)
        thread.start()
        
        return Response({
            'status': 'processing',
            'message': 'Notification resend started',
            'notification_id': str(notification.id)
        })
        
# Test endpoint for debugging URL routing
@api_view(['GET'])
def test_endpoint(request):
    """Simple test endpoint to verify URL routing works"""
    format_param = request.query_params.get('format', 'none')
    return Response({
        'message': 'Test endpoint working',
        'format': format_param,
        'query_params': dict(request.query_params)
    })

# Dedicated CSV download endpoint
@api_view(['GET'])
def download_document_csv(request, pk):
    """Direct CSV download endpoint"""
    print(f"DEBUG: CSV endpoint called with pk={pk}")
    try:
        document = Document.objects.get(id=pk)
        
        # Generate CSV
        import io
        import csv
        
        headers = []
        row_data = []
        
        # Add main document fields (always available)
        main_document_fields = ["filename", "status", "document_type", "detected_language", "uploaded_at", "summary"]
        for field in main_document_fields:
            headers.append(field)
            value = getattr(document, field, "")
            row_data.append(str(value))
        
        # Add extracted data if available
        if document.extracted_data:
            # Add validation status if it exists
            if 'validation_results' in document.extracted_data:
                headers.append("validation_status")
                row_data.append(str(document.extracted_data['validation_results'].get('status', '')))
            
            # Add extracted data fields - prioritize important fields first
            priority_fields = ['form_identifier', 'involved_party_1', 'involved_party_2_role', 'fields_identified']
            
            # Add priority fields first
            for key in priority_fields:
                if key in document.extracted_data:
                    headers.append(key)
                    row_data.append(str(document.extracted_data[key]))
            
            # Add any remaining extracted data fields
            for key, value in document.extracted_data.items():
                if key not in ['raw_text', 'validation_results'] + priority_fields:
                    headers.append(key)
                    row_data.append(str(value))
        else:
            # Add note that no data was extracted
            headers.append("extraction_note")
            row_data.append("No data extracted - document processing may have failed")
        
        # Write the final CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerow(row_data)
        csv_content = output.getvalue()
        
        # Create a direct HttpResponse with CSV content
        response = HttpResponse(
            content=csv_content,
            content_type='text/csv'
        )
        response['Content-Disposition'] = f'attachment; filename="{document.filename}_data.csv"'
        return response
        
    except Document.DoesNotExist:
        return Response(
            {'error': f'Document with ID {pk} not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Error in CSV download: {str(e)}")
        return Response(
            {'error': f'Error processing request: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Direct view function for document data download to handle query parameters properly
@api_view(['GET'])
def download_document_data(request, pk, format=None):
    """
    Direct view function for downloading extracted data in specified format (JSON, CSV, or XML)
    """
    print(f"DEBUG: download_document_data called with pk={pk}")
    print(f"DEBUG: query_params={dict(request.query_params)}")
    print(f"DEBUG: method={request.method}")
    try:
        # Try to get the document by ID
        try:
            document = Document.objects.get(id=pk)
        except Document.DoesNotExist:
            return Response(
                {'error': f'Document with ID {pk} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        if not document.extracted_data:
            return Response(
                {'error': 'No extracted data available for this document'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get requested format from URL parameter or query parameters (default to JSON)
        output_format = format or request.query_params.get('format', 'json')
        output_format = output_format.lower()
        
        # Validate format
        valid_formats = ['json', 'csv', 'xml']
        if output_format not in valid_formats:
            return Response(
                {'error': f'Invalid format. Supported formats: {", ".join(valid_formats)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if output_format == 'csv':
                # Initialize data structures
                headers = []
                row_data = []
                
                # Add main document fields
                main_document_fields = ["filename", "uploaded_file", "status", "document_type", 
                                       "detected_language", "summary", "uploaded_at"]
                headers.extend(main_document_fields)
                
                # Get corresponding values from document object
                for field in main_document_fields:
                    value = getattr(document, field, "")
                    row_data.append(str(value))
                    
                # Add validation status if it exists
                if document.extracted_data and 'validation_results' in document.extracted_data:
                    headers.append("validation_status")
                    row_data.append(str(document.extracted_data['validation_results'].get('status', '')))
                
                # Flatten the extracted data fields
                for key, value in document.extracted_data.items():
                    if key != 'raw_text' and key != 'validation_results':
                        headers.append(key)
                        row_data.append(str(value))
                
                # Write the final CSV
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(headers)
                writer.writerow(row_data)
                formatted_data = output.getvalue()
                
                # Create a direct HttpResponse with CSV content
                response = HttpResponse(
                    content=formatted_data,
                    content_type='text/csv'
                )
                response['Content-Disposition'] = f'attachment; filename="{document.filename}_data.csv"'
                return response
                
            elif output_format == 'json':
                # Return JSON directly
                formatted_data = json.dumps(document.extracted_data, indent=2)
                response = HttpResponse(
                    content=formatted_data,
                    content_type='application/json'
                )
                response['Content-Disposition'] = f'attachment; filename="{document.filename}_data.json"'
                return response
                
            else:
                # Convert data to XML using existing function
                formatted_data = convert_to_format(document.extracted_data, output_format)
                response = HttpResponse(
                    content=formatted_data,
                    content_type='application/xml'
                )
                response['Content-Disposition'] = f'attachment; filename="{document.filename}_data.xml"'
                return response
                
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        print(f"Error in download_document_data: {str(e)}")
        traceback.print_exc()
        return Response(
            {'error': f'Error processing request: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class IntegrationConfigurationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing integration configurations.
    """
    queryset = IntegrationConfiguration.objects.all().order_by('-created_at')
    serializer_class = IntegrationConfigurationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Set the created_by field when creating a new integration."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test connection to external system."""
        integration = self.get_object()
        
        def run_test():
            asyncio.run(self._test_integration_connection(integration.id))

        thread = threading.Thread(target=run_test)
        thread.daemon = True
        thread.start()

        return Response({'message': 'Connection test started'})

    async def _test_integration_connection(self, integration_id):
        """Test integration connection."""
        try:
            integration = await IntegrationConfiguration.objects.aget(id=integration_id)
            
            # Create a test document for connection testing
            test_document = type('TestDocument', (), {
                'id': 'test',
                'filename': 'test.pdf',
                'document_type': 'test',
                'extracted_data': {'test': 'data'},
                'summary': 'Test document for connection testing',
                'detected_language': 'en',
                'sentiment': 'neutral'
            })()
            
            # Test the connection
            result = await integration_service.send_to_external_system(test_document, integration)
            
            # Update integration status
            if result.get('status') == 'success':
                integration.status = 'active'
            else:
                integration.status = 'error'
            
            await integration.asave()
            print(f"Connection test result: {result}")
            
        except Exception as e:
            print(f"Error testing connection: {str(e)}")

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get integrations by type."""
        integration_type = request.query_params.get('type')
        if integration_type:
            integrations = self.queryset.filter(integration_type=integration_type)
        else:
            integrations = self.queryset.all()
        
        serializer = self.get_serializer(integrations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def audit_logs(self, request, pk=None):
        """Get audit logs for this integration."""
        integration = self.get_object()
        logs = IntegrationAuditLog.objects.filter(integration=integration).order_by('-started_at')
        serializer = IntegrationAuditLogSerializer(logs, many=True)
        return Response(serializer.data)


class IntegrationAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing integration audit logs.
    """
    queryset = IntegrationAuditLog.objects.all().order_by('-started_at')
    serializer_class = IntegrationAuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter logs by integration or document if specified."""
        queryset = super().get_queryset()
        integration_id = self.request.query_params.get('integration_id')
        document_id = self.request.query_params.get('document_id')
        
        if integration_id:
            queryset = queryset.filter(integration_id=integration_id)
        if document_id:
            queryset = queryset.filter(document_id=document_id)
            
        return queryset


class DocumentApprovalViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing document approvals.
    """
    queryset = DocumentApproval.objects.all().order_by('-assigned_at')
    serializer_class = DocumentApprovalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter approvals by user or status."""
        queryset = super().get_queryset()
        
        # Filter by current user's approvals
        if self.request.query_params.get('my_approvals'):
            queryset = queryset.filter(approver=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a document."""
        approval = self.get_object()
        comments = request.data.get('comments', '')
        
        def run_approval():
            asyncio.run(self._handle_approval(pk, 'approved', comments))

        thread = threading.Thread(target=run_approval)
        thread.daemon = True
        thread.start()

        return Response({'message': 'Approval processed'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a document."""
        approval = self.get_object()
        comments = request.data.get('comments', '')
        
        def run_rejection():
            asyncio.run(self._handle_approval(pk, 'rejected', comments))

        thread = threading.Thread(target=run_rejection)
        thread.daemon = True
        thread.start()

        return Response({'message': 'Rejection processed'})

    @action(detail=True, methods=['post'])
    def delegate(self, request, pk=None):
        """Delegate an approval to another user."""
        delegated_to_id = request.data.get('delegated_to_id')
        delegation_reason = request.data.get('delegation_reason', '')
        
        if not delegated_to_id:
            return Response({'error': 'delegated_to_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        def run_delegation():
            asyncio.run(self._handle_delegation(pk, delegated_to_id, delegation_reason))

        thread = threading.Thread(target=run_delegation)
        thread.daemon = True
        thread.start()

        return Response({'message': 'Delegation processed'})

    async def _handle_approval(self, approval_id, action, comments):
        """Handle approval action."""
        try:
            result = await workflow_service.handle_approval_response(
                approval_id, 
                self.request.user, 
                action, 
                comments
            )
            print(f"Approval result: {result}")
        except Exception as e:
            print(f"Error handling approval: {str(e)}")

    async def _handle_delegation(self, approval_id, delegated_to_id, delegation_reason):
        """Handle approval delegation."""
        try:
            approval = await DocumentApproval.objects.aget(id=approval_id)
            delegated_to = await User.objects.aget(id=delegated_to_id)
            
            approval.delegated_to = delegated_to
            approval.delegation_reason = delegation_reason
            approval.status = 'delegated'
            await approval.asave()
            
            # Create new approval for delegated user
            new_approval = DocumentApproval(
                document=approval.document,
                workflow_step=approval.workflow_step,
                approver=delegated_to,
                approval_level=approval.approval_level,
                due_date=approval.due_date
            )
            await new_approval.asave()
            
            print(f"Approval delegated to {delegated_to.username}")
            
        except Exception as e:
            print(f"Error handling delegation: {str(e)}")


class WorkflowExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing workflow executions.
    """
    queryset = WorkflowExecution.objects.all().order_by('-started_at')
    serializer_class = WorkflowExecutionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter executions by document or workflow."""
        queryset = super().get_queryset()
        document_id = self.request.query_params.get('document_id')
        workflow_id = self.request.query_params.get('workflow_id')
        
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        if workflow_id:
            queryset = queryset.filter(workflow_id=workflow_id)
            
        return queryset

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a workflow execution."""
        execution = self.get_object()
        
        if execution.status in ['completed', 'failed', 'cancelled']:
            return Response({'error': 'Cannot cancel completed workflow'}, status=status.HTTP_400_BAD_REQUEST)
        
        execution.status = 'cancelled'
        execution.completed_at = timezone.now()
        execution.save()
        
        return Response({'message': 'Workflow cancelled'})


class RealTimeSyncStatusViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing real-time sync status.
    """
    queryset = RealTimeSyncStatus.objects.all().order_by('-last_sync')
    serializer_class = RealTimeSyncStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter sync status by document or integration."""
        queryset = super().get_queryset()
        document_id = self.request.query_params.get('document_id')
        integration_id = self.request.query_params.get('integration_id')
        
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        if integration_id:
            queryset = queryset.filter(integration_id=integration_id)
            
        return queryset

    @action(detail=True, methods=['post'])
    def force_sync(self, request, pk=None):
        """Force sync for a document."""
        sync_status = self.get_object()
        
        def run_sync():
            asyncio.run(self._force_sync(sync_status.id))

        thread = threading.Thread(target=run_sync)
        thread.daemon = True
        thread.start()

        return Response({'message': 'Sync forced'})

    async def _force_sync(self, sync_status_id):
        """Force sync for a document."""
        try:
            sync_status = await RealTimeSyncStatus.objects.aget(id=sync_status_id)
            
            # Perform sync
            result = await integration_service.send_to_external_system(
                sync_status.document,
                sync_status.integration
            )
            
            # Update sync status
            sync_status.external_data = result
            sync_status.is_synced = result.get('status') == 'success'
            sync_status.retry_count = 0 if sync_status.is_synced else sync_status.retry_count + 1
            await sync_status.asave()
            
            print(f"Force sync result: {result}")
            
        except Exception as e:
            print(f"Error in force sync: {str(e)}")

    @action(detail=True, methods=['post'])
    def stop_sync(self, request, pk=None):
        """Stop real-time sync for a document."""
        sync_status = self.get_object()
        
        def run_stop():
            asyncio.run(sync_service.stop_sync(sync_status.document.id, sync_status.integration.id))

        thread = threading.Thread(target=run_stop)
        thread.daemon = True
        thread.start()

        return Response({'message': 'Sync stopped'})
