import asyncio
import threading
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer

# Import the AI services
from .services.classification_service import classify_document
from .services.extraction_service import extract_data
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
    This function will be executed in the background.
    """
    try:
        # Use .aget() for asynchronous database fetching within an async function
        document = await Document.objects.aget(id=document_id)
        print(f"Starting AI pipeline for {document.filename}...")

        # --- AI PROCESSING STEPS ---
        document.document_type = await classify_document(document.uploaded_file.path)
        extracted_data = await extract_data(document.uploaded_file.path)
        if extracted_data:
            # Store the structured data returned by our extraction service
            document.extracted_data = extracted_data
        document.summary = await summarize_document(document.uploaded_file.path)
        
        # --- FINAL STEP ---
        document.status = "processed"
        await document.asave()
        print(f"Successfully processed and saved document: {document.filename}")

    except Document.DoesNotExist:
        print(f"Error in pipeline: Document with id {document_id} not found.")
    except Exception as e:
        print(f"An error occurred in the processing pipeline for document {document_id}: {e}")
        try:
            document_to_fail = await Document.objects.aget(id=document_id)
            document_to_fail.status = "error"
            await document_to_fail.asave()
        except Document.DoesNotExist:
            pass # Document was likely deleted, nothing more to do.

class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows documents to be viewed or edited.
    """
    queryset = Document.objects.all().order_by('-uploaded_at')
    serializer_class = DocumentSerializer

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Custom synchronous action to handle file uploads.
        It immediately returns a response and starts the AI processing in the background.
        """
        # The key in request.FILES must match the key used in the frontend's FormData.
        # Let's assume the key is 'uploaded_file'.
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
