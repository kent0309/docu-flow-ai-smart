
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
