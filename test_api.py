try:
    import requests
except ImportError:
    print("The 'requests' package is not installed. Installing it now...")
    import subprocess
    subprocess.check_call(["pip", "install", "requests"])
    import requests

import json
import time
import os
import sys

# Base URL of the API
API_URL = "http://127.0.0.1:8000/api"

# Terminal colors for better output (Windows compatible)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color):
    print(f"{color}{text}{Colors.ENDC}")

def print_section(title):
    print("\n" + "="*50)
    print_colored(f" {title} ", Colors.HEADER + Colors.BOLD)
    print("="*50)

# Function to upload a document
def upload_document(file_path):
    filename = os.path.basename(file_path)
    print_colored(f"Uploading {filename}...", Colors.BLUE)
    
    with open(file_path, 'rb') as file:
        files = {'file': file}
        data = {'filename': filename}
        response = requests.post(f"{API_URL}/documents/", files=files, data=data)
    
    if response.status_code == 201:
        print_colored("✓ Document uploaded successfully!", Colors.GREEN)
        return response.json()
    else:
        print_colored(f"✗ Error uploading document: {response.status_code}", Colors.RED)
        print(response.text)
        return None

# Function to check document status
def check_document_status(document_id):
    response = requests.get(f"{API_URL}/documents/{document_id}/")
    if response.status_code == 200:
        return response.json()
    else:
        print_colored(f"✗ Error checking document status: {response.status_code}", Colors.RED)
        return None

# Function to list all documents
def list_documents():
    response = requests.get(f"{API_URL}/documents/")
    if response.status_code == 200:
        return response.json()
    else:
        print_colored(f"✗ Error listing documents: {response.status_code}", Colors.RED)
        return None

# Check if server is running
try:
    print_section("CHECKING SERVER CONNECTION")
    print("Attempting to connect to the Django server...")
    response = requests.get(f"{API_URL}/documents/")
    print_colored(f"✓ Server is running! Status code: {response.status_code}", Colors.GREEN)
except requests.exceptions.ConnectionError:
    print_colored("✗ ERROR: Cannot connect to the server at http://127.0.0.1:8000", Colors.RED)
    print("Please make sure the Django server is running with:")
    print_colored("  cd django_backend", Colors.YELLOW)
    print_colored("  .\\venv\\Scripts\\Activate.ps1", Colors.YELLOW)
    print_colored("  python manage.py runserver", Colors.YELLOW)
    sys.exit(1)

# Check what documents exist already
print_section("EXISTING DOCUMENTS")
docs = list_documents()
if docs:
    if len(docs) > 0:
        print(f"Found {len(docs)} existing documents:")
        for doc in docs:
            status_color = Colors.GREEN if doc['status'] == 'processed' else Colors.YELLOW if doc['status'] == 'processing' else Colors.RED
            print(f"- {doc['filename']} ({doc['document_type'] or 'unknown'}) - Status: {status_color}{doc['status']}{Colors.ENDC}")
    else:
        print("No documents found in the system.")
else:
    print_colored("✗ Error retrieving document list", Colors.RED)

# Upload the test invoice if it exists
print_section("DOCUMENT UPLOAD & PROCESSING")
test_file = "test_invoice.txt"
if not os.path.exists(test_file):
    print_colored(f"✗ Test file {test_file} not found", Colors.RED)
    sys.exit(1)

document = upload_document(test_file)

if document:
    document_id = document['id']
    print(f"Document ID: {document_id}")
    print_colored("Waiting for processing to complete...", Colors.YELLOW)
    
    # Poll for status updates
    for i in range(10):  # Try up to 10 times
        if i > 0:
            print(f"Checking status... (attempt {i+1}/10)")
        time.sleep(2)  # Wait 2 seconds between checks
        doc_status = check_document_status(document_id)
        
        if doc_status:
            status = doc_status['status']
            status_color = Colors.GREEN if status == 'processed' else Colors.YELLOW if status == 'processing' else Colors.RED
            print(f"Current status: {status_color}{status}{Colors.ENDC}")
            
            if status == 'processed':
                print_section("PROCESSING RESULTS")
                print_colored("✓ Document processing completed successfully!", Colors.GREEN)
                
                print_section("DOCUMENT DETAILS")
                print(f"Type: {doc_status['document_type'] or 'unknown'}")
                print(f"Confidence: {doc_status['confidence']}%") if doc_status['confidence'] else print("Confidence: N/A")
                
                print_section("EXTRACTED DATA")
                if doc_status['extracted_data']:
                    print(json.dumps(doc_status['extracted_data'], indent=2))
                else:
                    print("No data extracted")
                
                print_section("SUMMARY")
                if doc_status['summary']:
                    print(doc_status['summary'])
                else:
                    print("No summary generated")
                break
            elif status == 'error':
                print_colored("✗ Error processing document", Colors.RED)
                break
    else:
        print_colored("⚠ Timed out waiting for processing to complete", Colors.YELLOW)
        print("The document was uploaded but processing is taking longer than expected.")
        print(f"You can check the status later by visiting: http://127.0.0.1:8000/admin/api/document/{document_id}/change/")

print_section("NEXT STEPS")
print("1. View all documents in the API: http://127.0.0.1:8000/api/documents/")
print("2. Access the admin interface: http://127.0.0.1:8000/admin/")
print("   (You'll need to create a superuser with: python manage.py createsuperuser)")
print("3. Train custom models: python manage.py train_model") 