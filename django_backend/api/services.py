# django_backend/api/services.py
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from transformers import pipeline

# Initialize AI models. They will be downloaded on first use.
classifier = pipeline("document-question-answering", model="impira/layoutlm-document-qa")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def process_document_file(document_instance):
    try:
        text = extract_text_from_file(document_instance.file.path)
        if not text:
            document_instance.status = document_instance.Status.ERROR
            document_instance.save()
            return

        doc_type = classify_text(text)
        document_instance.document_type = doc_type

        # Summarize content in chunks
        max_chunk_length = 1024
        summary_text = ""
        for i in range(0, len(text), max_chunk_length):
            chunk = text[i:i + max_chunk_length]
            summary_part = summarizer(chunk, max_length=50, min_length=15, do_sample=False)
            summary_text += summary_part[0]['summary_text'] + " "
        document_instance.summary = summary_text.strip()

        # Example data extraction for invoices
        if doc_type == 'invoice':
            extracted_info = {}
            invoice_q = "What is the invoice number?"
            total_q = "What is the total amount?"

            invoice_number = classifier(question=invoice_q, context=text)
            total_amount = classifier(question=total_q, context=text)

            extracted_info['invoice_number'] = invoice_number.get('answer', 'Not found')
            extracted_info['total_amount'] = total_amount.get('answer', 'Not found')

            document_instance.extracted_data = extracted_info
            document_instance.confidence = (invoice_number.get('score', 0) + total_amount.get('score', 0)) / 2 * 100

        document_instance.status = document_instance.Status.PROCESSED
        document_instance.save()
    except Exception as e:
        print(f"Error processing document {document_instance.id}: {e}")
        document_instance.status = document_instance.Status.ERROR
        document_instance.save()

def extract_text_from_file(file_path):
    if file_path.lower().endswith('.pdf'):
        images = convert_from_path(file_path)
        return "".join([pytesseract.image_to_string(img) for img in images])
    else:
        return pytesseract.image_to_string(Image.open(file_path))

def classify_text(text):
    text_lower = text.lower()
    if "invoice" in text_lower: return "invoice"
    if "contract" in text_lower or "agreement" in text_lower: return "contract"
    if "receipt" in text_lower: return "receipt"
    return "other" 