import asyncio
import threading
import traceback
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document, Workflow, WorkflowStep, ValidationRule
from .serializers import DocumentSerializer, WorkflowSerializer, WorkflowStepSerializer, ValidationRuleSerializer
from django.http import Http404

# Import the AI services
from .services.classification_service import classify_document, detect_document_language
from langdetect.detector import LangDetectException
from .services.extraction_service import extract_data, extract_data_from_document, convert_to_format, validate_and_clean_data
from .services.nlp_service import summarize_document, semantic_document_understanding
from .services.workflow_service import (
    process_document_in_workflow, 
    create_workflow, 
    get_workflow_templates,
    send_workflow_notification
)
from .services.llm_service import process_document_with_llm
from .services.validation_service import validate_document_data

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
        
    @action(detail=True, methods=['get'])
    def download_extracted_data(self, request, pk=None):
        """
        Download extracted data in specified format (JSON, CSV, or XML)
        """
        document = self.get_object()
        if not document.extracted_data:
            return Response(
                {'error': 'No extracted data available for this document'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get requested format (default to JSON)
        output_format = request.query_params.get('format', 'json').lower()
        
        try:
            # Convert data to requested format
            formatted_data = convert_to_format(document.extracted_data, output_format)
            
            # Prepare response with appropriate content type
            content_types = {
                'json': 'application/json',
                'csv': 'text/csv',
                'xml': 'application/xml'
            }
            
            return Response(
                formatted_data, 
                content_type=content_types.get(output_format, 'text/plain'),
                headers={
                    'Content-Disposition': f'attachment; filename="{document.filename}_data.{output_format}"'
                }
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
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
        Optionally filter validation rules by document type or active status.
        """
        queryset = ValidationRule.objects.all().order_by('-created_at')
        
        # Filter by document type if provided
        document_type = self.request.query_params.get('document_type', None)
        if document_type is not None:
            queryset = queryset.filter(document_type=document_type)
            
        # Filter by active status if provided
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_active=is_active_bool)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def rule_types(self, request):
        """
        Get available rule types for creating validation rules.
        """
        rule_types = [
            {'value': choice[0], 'label': choice[1]} 
            for choice in ValidationRule.RULE_TYPE_CHOICES
        ]
        return Response({'rule_types': rule_types})
    
    @action(detail=False, methods=['get'])
    def by_document_type(self, request):
        """
        Get validation rules grouped by document type.
        """
        document_types = ValidationRule.objects.values_list('document_type', flat=True).distinct()
        grouped_rules = {}
        
        for doc_type in document_types:
            rules = ValidationRule.objects.filter(
                document_type=doc_type, 
                is_active=True
            ).order_by('field_name')
            serialized_rules = ValidationRuleSerializer(rules, many=True)
            grouped_rules[doc_type] = serialized_rules.data
            
        return Response(grouped_rules)
