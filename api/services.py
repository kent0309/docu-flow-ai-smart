# django_backend/api/services.py
import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from transformers import pipeline
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if Tesseract is installed and accessible
try:
    tesseract_version = pytesseract.get_tesseract_version()
    logger.info(f"Tesseract OCR version: {tesseract_version}")
except Exception as e:
    logger.warning(f"Tesseract OCR not found or not properly configured: {e}")
    logger.warning("Document OCR features will not work correctly without Tesseract.")
    logger.warning("Download and install from: https://github.com/UB-Mannheim/tesseract/wiki")
    logger.warning("On Windows, add Tesseract to PATH or set pytesseract.pytesseract.tesseract_cmd")

# Try to set Tesseract path for Windows (common installation location)
if os.name == 'nt':  # Windows
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            logger.info(f"Found Tesseract at: {path}")
            break

# Initialize AI models (lazy loading - will be downloaded on first use)
summarizer = None
classifier = None

def load_models():
    global summarizer, classifier
    if summarizer is None:
        logger.info("Loading summarization model...")
        try:
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        except Exception as e:
            logger.error(f"Error loading summarization model: {e}")
            summarizer = None
    
    if classifier is None:
        logger.info("Loading document-qa model...")
        try:
            classifier = pipeline("document-question-answering", model="impira/layoutlm-document-qa")
        except Exception as e:
            logger.error(f"Error loading document-qa model: {e}")
            classifier = None

def process_document_file(document_instance):
    try:
        # Extract text using OCR
        text = extract_text_from_file(document_instance.file.path)
        if not text:
            logger.warning(f"No text extracted from document {document_instance.id}")
            document_instance.status = document_instance.Status.ERROR
            document_instance.save()
            return

        # Classify document type
        doc_type = classify_text(text)
        document_instance.document_type = doc_type
        logger.info(f"Document classified as: {doc_type}")

        # Load AI models for processing
        load_models()
        
        # Summarize content
        if summarizer:
            try:
                # Summarize in chunks to handle large documents
                max_chunk_length = 1024
                summary_text = ""
                for i in range(0, len(text), max_chunk_length):
                    chunk = text[i:i + max_chunk_length]
                    summary_part = summarizer(chunk, max_length=50, min_length=15, do_sample=False)
                    summary_text += summary_part[0]['summary_text'] + " "
                document_instance.summary = summary_text.strip()
                logger.info(f"Generated summary of {len(summary_text)} characters")
            except Exception as e:
                logger.error(f"Error generating summary: {e}")
                document_instance.summary = "Error generating summary"
        else:
            document_instance.summary = "Summarization model not available"

        # Extract data from document
        if classifier and doc_type == 'invoice':
            try:
                extracted_info = {}
                invoice_q = "What is the invoice number?"
                total_q = "What is the total amount?"

                invoice_number = classifier(question=invoice_q, context=text)
                total_amount = classifier(question=total_q, context=text)

                extracted_info['invoice_number'] = invoice_number.get('answer', 'Not found')
                extracted_info['total_amount'] = total_amount.get('answer', 'Not found')

                document_instance.extracted_data = extracted_info
                document_instance.confidence = (invoice_number.get('score', 0) + total_amount.get('score', 0)) / 2 * 100
                logger.info(f"Extracted data from invoice: {extracted_info}")
            except Exception as e:
                logger.error(f"Error extracting data: {e}")
                document_instance.extracted_data = {"error": str(e)}
                document_instance.confidence = 0
        else:
            document_instance.extracted_data = {"message": "No data extraction performed"}
            document_instance.confidence = 0

        # Update status and save
        document_instance.status = document_instance.Status.PROCESSED
        document_instance.save()
        logger.info(f"Document {document_instance.id} processed successfully")
    except Exception as e:
        logger.error(f"Error processing document {document_instance.id}: {e}")
        document_instance.status = document_instance.Status.ERROR
        document_instance.save()

def extract_text_from_file(file_path):
    """Extract text from PDF or image files using OCR"""
    try:
        if file_path.lower().endswith('.pdf'):
            logger.info(f"Processing PDF file: {file_path}")
            try:
                # Convert PDF to images
                images = convert_from_path(file_path)
                logger.info(f"Converted PDF to {len(images)} images")
                
                # Extract text from each page
                text = ""
                for i, img in enumerate(images):
                    page_text = pytesseract.image_to_string(img)
                    text += page_text + "\n\n"
                    logger.info(f"Extracted text from page {i+1}")
                return text
            except Exception as e:
                logger.error(f"Error processing PDF: {e}")
                return None
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            logger.info(f"Processing image file: {file_path}")
            return pytesseract.image_to_string(Image.open(file_path))
        elif file_path.lower().endswith('.txt'):
            logger.info(f"Processing text file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            return None
    except Exception as e:
        logger.error(f"Error in text extraction: {e}")
        return None

def classify_text(text):
    """Classify document based on text content"""
    text_lower = text.lower()
    if "invoice" in text_lower: 
        return "invoice"
    if "contract" in text_lower or "agreement" in text_lower: 
        return "contract"
    if "receipt" in text_lower: 
        return "receipt"
    return "other" 