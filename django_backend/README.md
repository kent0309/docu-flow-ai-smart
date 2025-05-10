
# Document Processor API

A Django REST API for document processing, data extraction, and summarization using AI.

## Setup Instructions

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

## API Endpoints

- `GET /api/documents/`: List all documents
- `POST /api/documents/`: Upload a new document
- `GET /api/documents/{id}/`: Get document details
- `DELETE /api/documents/{id}/`: Delete a document
- `POST /api/documents/{id}/summarize/`: Generate a summary for a document
- `POST /api/documents/{id}/extract/`: Extract data from a document
- `GET /api/processed-documents/`: List all processed documents
- `GET /api/processed-documents/{id}/`: Get processed document details

## Dependencies

- Django and Django REST Framework for the API
- pytesseract for OCR
- pdf2image for PDF processing
- transformers library for AI-powered summarization
- PIL (Pillow) for image processing

## Note

This is a development setup. For production, you should:
- Use a production-ready database like PostgreSQL
- Configure proper security settings
- Set up Celery for background processing of documents
- Configure HTTPS
