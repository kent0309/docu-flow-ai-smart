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

# Base URL of the API
API_URL = "http://127.0.0.1:8000/api"

# Function to upload a document
def upload_document(file_path):
    filename = os.path.basename(file_path)
    print(f"Uploading {filename}...")
    
    with open(file_path, 'rb') as file:
        files = {'file': file}
        data = {'filename': filename}
        response = requests.post(f"{API_URL}/documents/", files=files, data=data)
    
    if response.status_code == 201:
        print("Document uploaded successfully!")
        return response.json()
    else:
        print(f"Error uploading document: {response.status_code}")
        print(response.text)
        return None

# Function to check document status
def check_document_status(document_id):
    response = requests.get(f"{API_URL}/documents/{document_id}/")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error checking document status: {response.status_code}")
        return None

# Check if server is running
try:
    print("Checking if the Django server is running...")
    response = requests.get(f"{API_URL}/documents/")
    print(f"Server is running! Status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to the server at http://127.0.0.1:8000")
    print("Please make sure the Django server is running with:")
    print("python manage.py runserver")
    exit(1)

# Upload the test invoice
document = upload_document("test_invoice.txt")

if document:
    document_id = document['id']
    print(f"Document ID: {document_id}")
    print("Waiting for processing to complete...")
    
    # Poll for status updates
    for _ in range(10):  # Try up to 10 times
        time.sleep(2)  # Wait 2 seconds between checks
        doc_status = check_document_status(document_id)
        
        if doc_status:
            status = doc_status['status']
            print(f"Current status: {status}")
            
            if status == 'processed':
                print("\nDocument processing completed!")
                print("\nDocument details:")
                print(f"Type: {doc_status['document_type']}")
                print(f"Confidence: {doc_status['confidence']}%")
                print("\nExtracted data:")
                print(json.dumps(doc_status['extracted_data'], indent=2))
                print("\nSummary:")
                print(doc_status['summary'])
                break
            elif status == 'error':
                print("Error processing document")
                break
    else:
        print("Timed out waiting for processing to complete") 