
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Document, ProcessedDocument
from .serializers import DocumentSerializer, ProcessedDocumentSerializer
from .services import document_processor

class DocumentListCreateView(generics.ListCreateAPIView):
    queryset = Document.objects.all().order_by('-uploaded_at')
    serializer_class = DocumentSerializer

class DocumentDetailView(generics.RetrieveDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class ProcessedDocumentListView(generics.ListAPIView):
    queryset = ProcessedDocument.objects.all().order_by('-processed_at')
    serializer_class = ProcessedDocumentSerializer

class ProcessedDocumentDetailView(generics.RetrieveAPIView):
    queryset = ProcessedDocument.objects.all()
    serializer_class = ProcessedDocumentSerializer

class SummarizeDocumentView(APIView):
    def post(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        processed_doc = document.processed
        
        if processed_doc.status == 'processing':
            return Response({'detail': 'Document is currently being processed'}, 
                            status=status.HTTP_409_CONFLICT)
        
        # Update status to processing
        processed_doc.status = 'processing'
        processed_doc.save()
        
        try:
            # Process the document asynchronously (in a real app, use Celery)
            summary = document_processor.summarize_document(document)
            
            # Update processed document with summary
            processed_doc.summary = summary
            processed_doc.status = 'completed'
            processed_doc.save()
            
            return Response({
                'id': processed_doc.id,
                'status': processed_doc.status,
                'summary': summary
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            processed_doc.status = 'failed'
            processed_doc.save()
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExtractDataView(APIView):
    def post(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        processed_doc = document.processed
        
        if processed_doc.status == 'processing':
            return Response({'detail': 'Document is currently being processed'}, 
                            status=status.HTTP_409_CONFLICT)
        
        # Update status to processing
        processed_doc.status = 'processing'
        processed_doc.save()
        
        try:
            # Process the document asynchronously (in a real app, use Celery)
            extracted_data = document_processor.extract_data(document)
            
            # Update processed document with extracted data
            processed_doc.extracted_data = extracted_data
            processed_doc.status = 'completed'
            processed_doc.save()
            
            return Response({
                'id': processed_doc.id,
                'status': processed_doc.status,
                'extracted_data': extracted_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            processed_doc.status = 'failed'
            processed_doc.save()
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TrainModelView(APIView):
    """API endpoint to trigger ML model training"""
    
    def post(self, request):
        try:
            # Start training process
            success = document_processor.train_ml_model()
            
            if success:
                return Response({
                    'status': 'success',
                    'message': 'Model training completed successfully'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'warning',
                    'message': 'Training skipped. Not enough data or model not improved'
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ModelStatsView(APIView):
    """API endpoint to get ML model statistics"""
    
    def get(self, request):
        try:
            # In a real implementation, this would fetch actual metrics from the model
            # For now, we'll return mock statistics
            return Response({
                'status': 'active',
                'documentTypes': ['Invoice', 'Financial Report', 'Contract', 'Receipt', 'General Document'],
                'totalDocumentsProcessed': 157,
                'accuracy': 92.5,
                'lastTrainingDate': '2025-05-01T14:32:45Z',
                'confidenceByDocType': {
                    'Invoice': 96.3,
                    'Financial Report': 94.1,
                    'Contract': 89.7,
                    'Receipt': 91.5,
                    'General Document': 83.2
                }
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
