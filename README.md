
# Document Processor - AI-Powered Document Processing System

A full-stack application for AI-powered document processing, data extraction, and summarization using React, Django, and machine learning.

## Project Overview

This application allows users to:
- Upload documents (PDF, DOCX, images)
- Extract structured data from documents using AI
- Generate document summaries
- Train ML models to improve document classification
- View processed documents and analytics

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Setup Instructions](#setup-instructions)
   - [Frontend Setup](#frontend-setup)
   - [Backend Setup](#backend-setup)
   - [Firebase Setup](#firebase-setup)
3. [Running the Application](#running-the-application)
4. [Project Structure](#project-structure)
5. [Technologies Used](#technologies-used)

## System Requirements

- Node.js (v18 or higher)
- Python (v3.8 or higher)
- pip (Python package manager)
- Git

## Setup Instructions

### Frontend Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Install frontend dependencies:
   ```
   npm install
   ```

3. Create a `.env` file in the project root with:
   ```
   VITE_API_URL=http://localhost:8000/api
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
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file with the following:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```

6. Run migrations:
   ```
   python manage.py migrate
   ```

### Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)

2. Enable Storage and Firestore in your Firebase project

3. Generate a Firebase service account key:
   - Go to Project Settings > Service Accounts
   - Click "Generate New Private Key"
   - Save the JSON file

4. Add Firebase credentials to Django backend:
   - Option 1: Save the JSON file in a secure location and add to `.env`:
     ```
     FIREBASE_CREDENTIALS_PATH=/path/to/your/serviceAccountKey.json
     ```
   - Option 2: Add the JSON content as a string in `.env`:
     ```
     FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project",...}
     ```

5. Update frontend Firebase config in `src/services/firebase.ts` with your Firebase project details

## Running the Application

### Start the Backend

1. From the `django_backend` directory with the virtual environment activated:
   ```
   python manage.py runserver
   ```
   The Django API will be available at http://localhost:8000/api/

### Start the Frontend

1. From the project root in a new terminal:
   ```
   npm run dev
   ```
   The React app will be available at http://localhost:5173/

## Project Structure

```
.
├── src/                    # Frontend React code
│   ├── components/         # React components
│   ├── config/             # Configuration files
│   ├── pages/              # Page components
│   ├── services/           # API service functions
│   └── ...
└── django_backend/         # Backend Django code
    ├── api/                # Django REST API app
    │   ├── models.py       # Database models
    │   ├── services/       # Business logic services
    │   ├── views.py        # API endpoints
    │   └── ...
    └── document_processor/ # Django project settings
```

## Technologies Used

### Frontend
- React
- TypeScript
- Tailwind CSS
- Shadcn UI
- Tanstack React Query

### Backend
- Django
- Django REST Framework
- Firebase (Storage & Firestore)
- Machine Learning libraries
  - scikit-learn
  - Transformers
  - PyTesseract (OCR)
  - PDF2Image

### AI & ML Features
- Document classification
- Text extraction (OCR)
- Document summarization
- Field extraction
