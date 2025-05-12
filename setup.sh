
#!/bin/bash

# Document Processor App Setup Script
echo "Setting up Document Processor Application..."

# Frontend setup
echo "Setting up Frontend..."
npm install

# Create frontend .env file
echo "Creating frontend .env file..."
cat > .env << EOL
VITE_API_URL=http://localhost:8000/api
EOL

echo "Frontend setup complete!"

# Backend setup
echo "Setting up Backend..."
cd django_backend

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create backend .env file
echo "Creating backend .env file..."
cat > .env << EOL
SECRET_KEY=django-insecure-development-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
MEDIA_ROOT=$(pwd)/media
UPLOAD_DIR=documents
DB_NAME=document_processor
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
EOL

# Create necessary directories
echo "Creating media directories..."
mkdir -p media/documents
mkdir -p media/training_data
mkdir -p models

# Run migrations
echo "Running database migrations..."
python manage.py migrate

echo "Backend setup complete!"
cd ..

echo "Setup completed successfully!"
echo "To start the application:"
echo "1. Start Django backend: cd django_backend && source venv/bin/activate && python manage.py runserver"
echo "2. Start React frontend: npm run dev"
