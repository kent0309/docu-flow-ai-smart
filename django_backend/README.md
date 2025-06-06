# DocuFlow AI - Django Backend

This is the backend component of the DocuFlow AI system, which processes documents using AI for classification, summarization, and data extraction.

## Features

- Document upload and processing
- AI-powered document classification
- Text extraction using OCR (Optical Character Recognition)
- Document summarization
- Data extraction from structured documents like invoices
- RESTful API for frontend integration

## Technologies Used

- Django 5.2
- Django REST Framework
- PyTesseract for OCR
- Transformers (Hugging Face) for AI models
- PDF2Image for PDF processing

## Setup Instructions

1. Clone the repository
2. Set up a Python virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   source venv/bin/activate     # Linux/Mac
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Install Tesseract OCR:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add to PATH or set the path in `api/services.py`

5. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
7. Start the server:
   ```
   python manage.py runserver
   ```

## API Endpoints

- `GET /api/documents/` - List all documents
- `POST /api/documents/` - Upload a new document
- `GET /api/documents/{id}/` - Get document details
- `DELETE /api/documents/{id}/` - Delete a document

## Training Custom Models

You can train custom document classification models with:

```
python manage.py train_model
```

This will create a model that can be used for improved document classification.

## License

MIT 