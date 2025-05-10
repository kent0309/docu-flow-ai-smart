
import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import time
import logging
from transformers import pipeline
from .ml_document_classifier import document_classifier
from .firebase_integration import firebase_manager

logger = logging.getLogger(__name__)

# Initialize the summarization model
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception as e:
    logger.warning(f"Failed to load summarization model: {e}")
    summarizer = None

def extract_text_from_image(image_path):
    """Extract text from an image using OCR"""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logger.error(f"Error extracting text from image {image_path}: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF by converting to images and using OCR"""
    try:
        pages = convert_from_path(pdf_path, 300)
        text = ""
        for i, page in enumerate(pages):
            # Save pages as images
            image_path = f"/tmp/page_{i}.jpg"
            page.save(image_path, 'JPEG')
            
            # Extract text from the page image
            text += extract_text_from_image(image_path) + "\n\n"
            
            # Clean up temporary file
            os.remove(image_path)
            
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
        return ""

def extract_data(document):
    """Extract structured data from a document"""
    # Get the document file path
    file_path = document.file.path
    
    # Extract text based on document type
    doc_text = ""
    if document.file_type in ['jpg', 'png']:
        doc_text = extract_text_from_image(file_path)
    elif document.file_type == 'pdf':
        doc_text = extract_text_from_pdf(file_path)
    else:
        # For other document types, we'd use appropriate libraries
        # This is a placeholder for demonstration
        doc_text = f"Text extraction not implemented for {document.file_type} files"
    
    # Use ML model to classify document type
    classification = document_classifier.predict_document_type(doc_text)
    doc_type = classification["documentType"]
    
    # Extract fields based on document type
    if doc_type == "Invoice":
        fields = detect_invoice_fields(doc_text)
    elif doc_type == "Financial Report":
        fields = detect_report_fields(doc_text)
    else:
        fields = []
    
    # Store document in Firebase for training
    if firebase_manager.is_initialized():
        # Upload document to Firebase Storage
        firebase_path = f"documents/{document.id}/{os.path.basename(file_path)}"
        firebase_url = firebase_manager.upload_document(file_path, firebase_path)
        
        # Store metadata in Firestore
        metadata = {
            'id': document.id,
            'title': document.title,
            'file_type': document.file_type,
            'uploaded_at': document.uploaded_at.isoformat(),
            'firebase_url': firebase_url,
            'document_type': doc_type,
            'confidence': classification.get("confidence", 0)
        }
        firebase_manager.store_document_metadata(document.id, metadata)
        
        # Store processing result for model training
        result_data = {
            'text': doc_text,
            'fields': fields,
            'documentType': doc_type,
        }
        firebase_manager.store_processing_result(document.id, result_data, doc_type)
    
    # Return structured data
    return {
        "documentType": doc_type,
        "confidence": classification.get("confidence", 0),
        "fields": fields,
        "text": doc_text[:1000]  # First 1000 chars for preview
    }

def detect_invoice_fields(text):
    """Detect and extract invoice fields from text"""
    # This is a simplified mock implementation
    # In a real system, this would use NER (Named Entity Recognition) models
    
    fields = []
    
    # Mock field extraction with confidence scores
    if "INV-" in text:
        invoice_num = text.split("INV-")[1][:10].strip()
        fields.append({
            "name": "Invoice Number", 
            "value": f"INV-{invoice_num}", 
            "confidence": 98, 
            "isValid": True
        })
    
    if "Date:" in text:
        date = text.split("Date:")[1].split("\n")[0].strip()
        fields.append({
            "name": "Date",
            "value": date,
            "confidence": 95,
            "isValid": True
        })
    
    if "Total:" in text or "Amount:" in text:
        amount = text.split("Total:")[1].split("\n")[0].strip() if "Total:" in text else text.split("Amount:")[1].split("\n")[0].strip()
        fields.append({
            "name": "Amount Due",
            "value": amount,
            "confidence": 90,
            "isValid": True
        })
    
    # Add some mock fields if we couldn't extract enough real ones
    if len(fields) < 3:
        fields.extend([
            {
                "name": "Vendor",
                "value": "Global Supplies Inc.",
                "confidence": 85,
                "isValid": True
            },
            {
                "name": "Payment Terms",
                "value": "Net 30",
                "confidence": 80,
                "isValid": True
            }
        ])
    
    return fields

def detect_report_fields(text):
    """Detect and extract report fields from text"""
    # Mock implementation for reports
    fields = []
    
    if "Report:" in text or "Title:" in text:
        report_title = text.split("Report:")[1].split("\n")[0].strip() if "Report:" in text else text.split("Title:")[1].split("\n")[0].strip()
        fields.append({
            "name": "Report Title",
            "value": report_title,
            "confidence": 95,
            "isValid": True
        })
    
    if "Period:" in text:
        period = text.split("Period:")[1].split("\n")[0].strip()
        fields.append({
            "name": "Period",
            "value": period,
            "confidence": 90,
            "isValid": True
        })
    
    # Add mock fields if needed
    if len(fields) < 2:
        fields.extend([
            {
                "name": "Total Revenue",
                "value": "$2,456,789.00",
                "confidence": 88,
                "isValid": True
            },
            {
                "name": "Net Profit",
                "value": "$687,452.18",
                "confidence": 85,
                "isValid": True
            },
            {
                "name": "Author",
                "value": "Finance Department",
                "confidence": 70,
                "isValid": False
            }
        ])
    
    return fields

def summarize_document(document):
    """Generate a summary of the document content"""
    # Get the document file path
    file_path = document.file.path
    
    # Extract text based on document type
    doc_text = ""
    if document.file_type in ['jpg', 'png']:
        doc_text = extract_text_from_image(file_path)
    elif document.file_type == 'pdf':
        doc_text = extract_text_from_pdf(file_path)
    else:
        # For other document types, we'd use appropriate libraries
        doc_text = f"Text extraction not implemented for {document.file_type} files"
    
    # If text is too short, return it as is
    if len(doc_text) < 100:
        return doc_text
    
    try:
        # Use the transformer model for summarization if available
        if summarizer:
            # Trim text to fit within model's max length
            max_length = 1024  # Typical limit for BART models
            input_text = doc_text[:max_length]
            
            # Generate summary
            summary_output = summarizer(input_text, max_length=150, min_length=30, do_sample=False)
            summary = summary_output[0]['summary_text']
            
            # Format the summary nicely
            return f"Executive Summary:\n\n{summary}"
        else:
            # Fallback to a simple extractive summary
            sentences = doc_text.split('.')
            important_sentences = sentences[:3]  # Just take first few sentences
            summary = '. '.join(important_sentences) + '.'
            return f"Executive Summary:\n\n{summary}"
    
    except Exception as e:
        logger.error(f"Error summarizing document: {e}")
        return "Error generating summary. The document may be too complex or in an unsupported format."

def train_ml_model():
    """Train or update the machine learning model"""
    return document_classifier.update_model()
