import joblib
import os

import numpy as np
from langdetect import detect, LangDetectException
import re

# Path to the classification model

from langdetect import detect, LangDetectException

model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml_models', 'document_classifier_pipeline.joblib')
try:
    classifier_pipeline = joblib.load(model_path)
    print(f"Classification model loaded successfully from {model_path}")
except FileNotFoundError:
    print(f"WARNING: Classification model not found at {model_path}. Please run the training script.")
    classifier_pipeline = None

# Dictionary mapping language codes to full names
LANGUAGE_MAPPING = {
    'en': 'English',
    'es': 'Spanish',
    'zh-cn': 'Mandarin',
    'zh-tw': 'Mandarin',
    'ms': 'Malay',
    'id': 'Indonesian',  # Often similar to Malay
    'ar': 'Arabic',
    'fr': 'French',
    'de': 'German',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ru': 'Russian',
    'pt': 'Portuguese',
    'it': 'Italian',
    'nl': 'Dutch',
    'hi': 'Hindi',
    'tr': 'Turkish',
    'vi': 'Vietnamese',
    'th': 'Thai'
}

# Mapping of document types to more specific subtypes
DOCUMENT_SUBTYPES = {
    'invoice': ['commercial_invoice', 'tax_invoice', 'proforma_invoice', 'service_invoice'],
    'receipt': ['payment_receipt', 'purchase_receipt', 'cash_receipt', 'digital_receipt'],
    'form': ['application_form', 'registration_form', 'feedback_form', 'survey_form'],
    'contract': ['employment_contract', 'service_agreement', 'rental_agreement', 'sales_contract'],
    'letter': ['cover_letter', 'recommendation_letter', 'business_letter', 'resignation_letter'],
    'resume': ['cv', 'professional_resume', 'academic_cv', 'portfolio'],
    'report': ['financial_report', 'progress_report', 'audit_report', 'technical_report'],
    'legal': ['affidavit', 'court_filing', 'legal_notice', 'power_of_attorney'],
    'email': ['business_email', 'personal_email', 'notification_email', 'promotional_email']
}

# Keywords to identify document types
DOCUMENT_TYPE_KEYWORDS = {
    'invoice': [
        'invoice', 'bill', 'statement', 'amount due', 'payment due', 'invoice no', 'invoice number',
        'total amount', 'subtotal', 'billing', 'tax invoice', 'due date', 'invoice date',
        'amount', 'due', 'payment terms', 'billed to', 'sold to', 'ship to'
    ],
    'receipt': ['receipt', 'received', 'payment received', 'paid', 'transaction'],
    'form': ['form', 'application', 'registration', 'please fill', 'survey', 'questionnaire'],
    'contract': ['contract', 'agreement', 'terms and conditions', 'parties', 'obligations'],
    'report': ['report', 'analysis', 'findings', 'results', 'conclusion', 'financial report'],
    'legal': ['legal', 'law', 'court', 'plaintiff', 'defendant', 'attorney'],
    'email': ['from:', 'to:', 'subject:', 'sent:', 'cc:', 'bcc:', 'forwarded message', 'reply',
              'email', 'inbox', 'gmail', 'outlook', 'message', 'sender', 'recipient']
}

def classify_document(text_content):
    """
    Classify document type based on its content.
    
    Args:
        text_content (str): Extracted text content from the document
        
    Returns:
        str: Classified document type
    """
    if not text_content:
        return "unknown"
    
    try:
        # First check for email specific patterns
        if is_email_document(text_content):
            return "email"
            
        # Then try keyword-based classification for common document types
        doc_type = keyword_based_classification(text_content)
        if doc_type and doc_type != "unknown":
            return doc_type
            
        # Try to identify specialized documents if keywords didn't work
        specialized = identify_specialized_document(text_content)
        if specialized:
            return specialized
            
        # If no keywords matched and we have a trained model, use ML classification
        if classifier_pipeline:
            # Basic classification
            prediction = classifier_pipeline.predict([text_content])
            doc_type = prediction[0]
            
            # Get prediction probabilities to check confidence
            proba = classifier_pipeline.predict_proba([text_content])[0]
            max_proba = max(proba)
            
            # If confidence is low, return "unknown" or "other"
            if max_proba < 0.7:  # Threshold for accepting classification
                return "other" if max_proba > 0.4 else "unknown"
            
            # Try to determine the specific subtype
            subtype = determine_document_subtype(doc_type, text_content)
            if subtype:
                return subtype
            
            return doc_type
        else:
            return "unknown"
    except Exception as e:
        print(f"Error during classification: {e}")
        return "unknown"

def is_email_document(text_content):
    """
    Determines if the document is an email based on common email patterns.
    
    Args:
        text_content (str): The text content of the document
        
    Returns:
        bool: True if the document appears to be an email, False otherwise
    """
    text_lower = text_content.lower()
    
    # Check for common email header patterns
    email_header_patterns = [
        r'from:\s*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        r'to:\s*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        r'subject:',
        r'sent:\s*(?:mon|tue|wed|thu|fri|sat|sun)',
        r'date:\s*(?:mon|tue|wed|thu|fri|sat|sun)',
        r'cc:',
        r'bcc:',
        r'reply-to:'
    ]
    
    # If two or more email header patterns are found, it's likely an email
    header_matches = sum(1 for pattern in email_header_patterns if re.search(pattern, text_lower))
    if header_matches >= 2:
        return True
    
    # Check for email addresses with @ symbol
    email_addresses = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text_content)
    if len(email_addresses) >= 2:  # If there are multiple email addresses, likely an email
        return True
        
    # Check for forwarded or replied email indicators
    if any(phrase in text_lower for phrase in ['forwarded message', 'original message', 'wrote:', 'reply']):
        return True
    
    return False

def keyword_based_classification(text_content):
    """
    Classify document based on keyword matching.
    
    Args:
        text_content (str): Text content from the document
        
    Returns:
        str: Document type or 'unknown'
    """
    text_lower = text_content.lower()
    
    # Count occurrences of keywords for each document type
    type_scores = {}
    for doc_type, keywords in DOCUMENT_TYPE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        type_scores[doc_type] = score
    
    # Find document type with highest keyword score, if any keywords were found
    max_score = max(type_scores.values()) if type_scores else 0
    if max_score > 0:
        # Get the document type with the highest score
        best_match = max(type_scores.items(), key=lambda x: x[1])[0]
        return best_match
    
    return "unknown"

def determine_document_subtype(doc_type, text_content):
    """
    Determine a more specific document subtype based on the main type and content.
    
    Args:
        doc_type (str): The main document type
        text_content (str): The document text content
        
    Returns:
        str or None: The specific subtype, or None if cannot determine
    """
    if doc_type not in DOCUMENT_SUBTYPES:
        return None
        
    # Convert text to lowercase for easier matching
    text_lower = text_content.lower()
    
    # Define subtype specific keywords
    subtype_keywords = {
        # Invoice subtypes
        'commercial_invoice': ['commercial invoice', 'export invoice', 'shipping invoice', 'international'],
        'tax_invoice': ['tax invoice', 'gst', 'vat', 'tax identification', 'tax id'],
        'proforma_invoice': ['proforma', 'pro forma', 'quote', 'quotation'],
        'service_invoice': ['service invoice', 'consultation', 'labor', 'professional services'],
        
        # Receipt subtypes
        'payment_receipt': ['payment received', 'payment receipt', 'received payment'],
        'purchase_receipt': ['purchase', 'bought', 'item purchased', 'retail'],
        'cash_receipt': ['cash payment', 'paid in cash', 'cash receipt'],
        'digital_receipt': ['electronic receipt', 'online purchase', 'e-receipt'],
        
        # Contract subtypes
        'employment_contract': ['employment', 'job offer', 'position', 'salary', 'work hours'],
        'service_agreement': ['service agreement', 'services provided', 'service terms'],
        'rental_agreement': ['rent', 'lease', 'tenant', 'landlord', 'property'],
        'sales_contract': ['purchase agreement', 'buyer', 'seller', 'sale of', 'sold to'],
        
        # Email subtypes
        'business_email': ['meeting', 'project', 'report', 'client', 'deadline', 'business'],
        'personal_email': ['hello', 'hi', 'hey', 'personal', 'family', 'friend'],
        'notification_email': ['notification', 'alert', 'update', 'confirm', 'verify', 'action required'],
        'promotional_email': ['offer', 'discount', 'sale', 'promotion', 'limited time', 'exclusive']
    }
    
    # Check for each subtype in the document type
    for subtype in DOCUMENT_SUBTYPES[doc_type]:
        if subtype in subtype_keywords:
            keywords = subtype_keywords[subtype]
            # Check if any of the subtype's keywords appear in the text
            if any(keyword in text_lower for keyword in keywords):
                return subtype
    
    # If we couldn't determine a specific subtype, return the general type
    return doc_type

def identify_specialized_document(text_content):
    """
    Identify specialized document types not covered by the main classifier.
    
    Args:
        text_content (str): The document text content
        
    Returns:
        str or None: The specialized document type, or None if not identified
    """
    # Convert text to lowercase for easier matching
    text_lower = text_content.lower()
    
    # Check for email patterns first
    if is_email_document(text_content):
        return "email"
    
    # Financial keywords that strongly indicate an invoice
    invoice_indicators = [
        r'(operating expenses|net profit|cash reserves|revenue|total\s+amount)',
        r'(invoice|bill|statement)\s+(#|no|number)',
        r'(total|amount)\s*:\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        r'(due date|payment date|invoice date)',
        r'(payment\s+terms|payment\s+due)',
        r'(sold\s+to|ship\s+to|bill\s+to|customer|client)'
    ]
    
    # Check for invoice indicators
    for pattern in invoice_indicators:
        if re.search(pattern, text_lower):
            return "invoice"
    
    # Other specialized documents
    if re.search(r'certificate\s+of\s+(incorporation|registration|formation)', text_lower):
        return "certificate"
    elif re.search(r'(press\s+release|for\s+immediate\s+release)', text_lower):
        return "press_release"
    elif re.search(r'(meeting\s+minutes|minutes\s+of\s+meeting|attendees|meeting\s+notes)', text_lower):
        return "meeting_minutes"
    elif re.search(r'(patent\s+application|intellectual\s+property|invention|claim)', text_lower):
        return "patent"
    elif re.search(r'(financial\s+statement|balance\s+sheet|income\s+statement)', text_lower):
        return "financial_statement"
    elif re.search(r'(proposal|quotation|bid|offer)', text_lower):
        return "proposal"
    
    return None

def detect_document_language(text_content):
    """
    Detect the language of a document's content.
    
    Args:
        text_content (str): The text content to analyze
        
    Returns:
        str: Detected language code or name, or "unknown" if detection fails
    """
    try:
        if text_content and len(text_content.strip()) > 20:
            # Use langdetect to identify the language code
            lang_code = detect(text_content)
            
            # Return the full language name if available, otherwise return the code
            return LANGUAGE_MAPPING.get(lang_code, lang_code)
        else:
            return "unknown"
    except LangDetectException:
        return "unknown"

def get_language_confidence(text_content, target_languages=None):
    """
    Get confidence scores for language detection.
    
    Args:
        text_content (str): The text content to analyze
        target_languages (list): Optional list of language codes to focus on
        
    Returns:
        dict: Language confidence scores
    """
    # This is a placeholder - in a real implementation, you would use a 
    # language detection library that provides confidence scores
    
    # For now, we'll return a simple dict with the detected language at high confidence
    try:
        if text_content and len(text_content.strip()) > 20:
            detected = detect(text_content)
            
            # Build a confidence dict with the detected language at high confidence
            confidence = {lang: 0.1 for lang in LANGUAGE_MAPPING.keys()}
            confidence[detected] = 0.9
            
            return confidence
        else:
            return {}
    except LangDetectException:
        return {}
def classify_document(text_content):
    if not classifier_pipeline or not text_content:
        return "unknown"
    try:
        prediction = classifier_pipeline.predict([text_content])
        return prediction[0]
    except Exception as e:
        print(f"Error during classification: {e}")
        return "error"

def detect_document_language(text_content):
    try:
        if text_content and len(text_content.strip()) > 20:
            return detect(text_content)
        return "unknown"
    except LangDetectException:
        return "unknown"
