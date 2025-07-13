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
from .services.classification_service import classify_document
from .services.extraction_service import extract_data, extract_data_from_document
from .services.nlp_service import summarize_document

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
