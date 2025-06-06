from django.shortcuts import render
from rest_framework import generics
from .models import Document
from .serializers import DocumentSerializer
from .services import process_document_file
import threading

# Create your views here.

class DocumentListCreateView(generics.ListCreateAPIView):
    queryset = Document.objects.all().order_by('-uploaded_at')
    serializer_class = DocumentSerializer

    def perform_create(self, serializer):
        document = serializer.save()
        # Process the document in a background thread to avoid blocking the API response
        thread = threading.Thread(target=process_document_file, args=(document,))
        thread.start()

class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
