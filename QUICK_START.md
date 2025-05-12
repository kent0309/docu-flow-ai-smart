
# Document Processor - Quick Start Guide

This guide provides the fastest way to get the Document Processor application up and running.

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.8 or higher)
- Git

## Automated Setup (Linux/Mac)

1. Clone the repository and navigate into the project folder

2. Run the setup script:
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

3. Start the backend:
   ```
   cd django_backend
   source venv/bin/activate
   python manage.py runserver
   ```

4. In a new terminal, start the frontend:
   ```
   npm run dev
   ```

5. Access the application at http://localhost:5173

## Manual Setup

If the automated setup doesn't work for you, follow these steps:

### Frontend Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Create a `.env` file in the project root:
   ```
   VITE_API_URL=http://localhost:8000/api
   ```

3. Start the development server:
   ```
   npm run dev
   ```

### Backend Setup

1. Navigate to the Django backend directory:
   ```
   cd django_backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file:
   ```
   SECRET_KEY=django-insecure-development-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   MEDIA_ROOT=/absolute/path/to/django_backend/media
   UPLOAD_DIR=documents
   ```

6. Create necessary directories:
   ```
   mkdir -p media/documents
   mkdir -p media/training_data
   mkdir -p models
   ```

7. Run migrations:
   ```
   python manage.py migrate
   ```

8. Start the development server:
   ```
   python manage.py runserver
   ```

## Using the Application

1. Upload documents on the Upload page
2. View processed documents on the Documents page
3. Train the ML model by clicking "Train Model Now" on the Dashboard

## Training Your Own Dataset

1. Place your training documents in the media/training_data directory
2. Format your text files with "DOCUMENT_TYPE: [Type]" as the first line
3. Run the training command:
   ```
   python manage.py train_model
   ```

## Troubleshooting

- If you encounter errors related to missing libraries, ensure all dependencies are installed
- For OCR functionality, make sure Tesseract OCR is installed on your system
- Check the Django and frontend logs for detailed error messages
