# Document Processing Backend

This is the backend service for document processing with AI capabilities, including classification, extraction, and analysis using Google Gemini 2.5 Flash.

## Getting Started

### Prerequisites

- Python 3.9+
- Django 4.2+
- Google API Key for Gemini 2.5 Flash

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd doc-processing-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your Google API key:
```
DJANGO_SECRET_KEY=your-django-secret-key
DEBUG=True
GOOGLE_API_KEY=your-google-api-key
```

### Setting up Google Gemini 2.5 Flash

1. Visit [Google AI Studio](https://ai.google.dev/) and sign up for an account.
2. Create an API key for Google Gemini 2.5 Flash.
3. Add the API key to your `.env` file as shown above.

### Running the Server

1. Apply migrations:
```bash
python manage.py migrate
```

2. Run the development server:
```bash
python manage.py runserver
```

## Features

- Document classification using Google Gemini 2.5 Flash
- Data extraction from various document types
- Text summarization and analysis
- Workflow-based document processing
- RESTful API endpoints for document management

## API Endpoints

- `POST /api/documents/upload/`: Upload a new document
- `GET /api/documents/`: List all documents
- `GET /api/documents/{id}/`: Get document details
- `GET /api/documents/{id}/download_extracted_data/?format=[json|csv|xml]`: Download extracted data
- `GET /api/documents/{id}/semantic_analysis/`: Perform semantic analysis
- `POST /api/documents/{id}/process_workflow/`: Process document through a workflow

## Environment Variables

- `DJANGO_SECRET_KEY`: Django secret key for cryptographic signing
- `DEBUG`: Debug mode flag (True/False)
- `GOOGLE_API_KEY`: API key for Google Gemini 2.5 Flash 