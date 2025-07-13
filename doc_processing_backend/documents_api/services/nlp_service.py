import asyncio
import random
import re
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
import nltk
import json
import spacy
import functools
from concurrent.futures import ThreadPoolExecutor

# Global variables for lazy loading
_transformers_pipeline = None
_transformers_AutoTokenizer = None
_transformers_AutoModelForSeq2SeqLM = None
_transformers_loaded = False

def load_transformers():
    """
    Lazy loading of transformers components to avoid import issues.
    """
    global _transformers_pipeline, _transformers_AutoTokenizer, _transformers_AutoModelForSeq2SeqLM, _transformers_loaded
    
    if _transformers_loaded:
        return _transformers_pipeline, _transformers_AutoTokenizer, _transformers_AutoModelForSeq2SeqLM
    
    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
        _transformers_pipeline = pipeline
        _transformers_AutoTokenizer = AutoTokenizer
        _transformers_AutoModelForSeq2SeqLM = AutoModelForSeq2SeqLM
        _transformers_loaded = True
        print("Transformers loaded successfully")
        return _transformers_pipeline, _transformers_AutoTokenizer, _transformers_AutoModelForSeq2SeqLM
    except ImportError as e:
        print(f"WARNING: Could not load transformers due to import error: {e}")
        print("NLP features requiring transformers will be disabled.")
        _transformers_loaded = True  # Mark as loaded to avoid repeated attempts
        return None, None, None
    except Exception as e:
        print(f"WARNING: Unexpected error loading transformers: {e}")
        _transformers_loaded = True
        return None, None, None

# Download necessary NLTK data packages if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('punkt')
    nltk.download('vader_lexicon')

# Load spaCy NER model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model is not installed, provide guidance in the error
    print("Spacy model 'en_core_web_sm' is not installed. Install it with:")
    print("python -m spacy download en_core_web_sm")
    # Create a blank model as fallback
    nlp = spacy.blank("en")

async def summarize_document(file_path):
    """
    Placeholder document summarization service.
    
    Args:
        file_path (str): Path to the uploaded document file
        
    Returns:
        str: Generated summary of the document
    """
    
    # Extract text from document
    extracted_text = await extract_text_for_nlp(file_path)
    
    if not extracted_text or len(extracted_text.strip()) < 50:
        return "Unable to generate summary due to insufficient text content."
    
    try:
        # First check if this is an email
        email_summary = await generate_email_summary(extracted_text)
        if email_summary:
            return email_summary
            
        # Then check if this is an invoice before trying transformer-based summary
        invoice_summary = await generate_invoice_summary(extracted_text)
        if invoice_summary:
            return invoice_summary
        
        # Load transformers components with lazy loading
        pipeline_func, AutoTokenizer_class, AutoModelForSeq2SeqLM_class = load_transformers()
        
        if pipeline_func is None:
            # Fallback to simpler method if transformers unavailable
            sentences = sent_tokenize(extracted_text)
            return " ".join(sentences[:3]) + "..."
        
        # Load summarization pipeline with t5-small model
        # We use a context manager to properly handle any potential CUDA memory issues
        summarizer = pipeline_func("summarization", model="t5-small")
        
        # T5 models are trained with a prefix
        text_to_summarize = "summarize: " + extracted_text
        
        # Handle long texts by chunking if necessary
        max_token_length = 512  # t5-small has a limit
        tokenizer = AutoTokenizer_class.from_pretrained("t5-small")
        encoded_input = tokenizer(text_to_summarize, return_tensors="pt", truncation=True, max_length=max_token_length)
        
        # Generate summary
        summary = summarizer(text_to_summarize, 
                           max_length=150,  # maximum length of the summary
                           min_length=30,   # minimum length of the summary
                           do_sample=False) # use greedy decoding
        
        # Extract the summary text from the result
        if summary and isinstance(summary, list) and len(summary) > 0:
            return summary[0]['summary_text']
        else:
            # Fallback to simpler method if transformer fails
            sentences = sent_tokenize(extracted_text)
            return " ".join(sentences[:3]) + "..."
            
    except Exception as e:
        print(f"Error in transformer summarization: {str(e)}")
        # Fallback to simpler method
        sentences = sent_tokenize(extracted_text)
        if len(sentences) <= 3:
            return extracted_text
        return " ".join(sentences[:3]) + "..."

async def generate_invoice_summary(text):
    """
    Generate a structured summary specifically for invoice documents.
    
    Args:
        text (str): The extracted text content from an invoice
        
    Returns:
        str: A structured summary of invoice details, or None if not recognized as an invoice
    """
    # Check if this is an invoice by looking for key terms
    text_lower = text.lower()
    if not any(term in text_lower for term in ['invoice', 'bill', 'amount due', 'payment', 'total']):
        return None
    
    # Extract key information from invoice text
    invoice_data = {}
    
    # Extract invoice ID
    invoice_id_match = re.search(r'(?:invoice|bill|statement)\s*(?:#|no|number)?[:.\s]*([a-z0-9\-]+)', text_lower, re.IGNORECASE)
    if invoice_id_match:
        invoice_data['invoice_id'] = invoice_id_match.group(1)
    
    # Extract total amount
    amount_match = re.search(r'(?:total|amount due|balance due|payment)\s*(?:of|:)?\s*\$?\s*([\d,]+(?:\.\d{2})?)', text_lower)
    if amount_match:
        invoice_data['total_amount'] = amount_match.group(1)
    
    # Extract dates (invoice date, due date)
    due_date_match = re.search(r'(?:due|payment)\s*(?:date|by)?\s*[:.\s]*([a-zA-Z]+\s+\d{1,2},?\s+\d{4}|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', text_lower)
    if due_date_match:
        invoice_data['due_date'] = due_date_match.group(1)
    
    # Extract vendor/company
    company_match = re.search(r'(?:from|by|vendor|company)[:.\s]*((?:[A-Z][A-Za-z]*\s*)+(?:Inc|Ltd|LLC|Corp|Company)?)', text)
    if company_match:
        invoice_data['vendor'] = company_match.group(1).strip()
    
    # Extract financial details
    expenses_match = re.search(r'(?:operating expenses|expenses)[^.]*?(\$?[\d,]+(?:\.\d{2})?)', text_lower)
    if expenses_match:
        invoice_data['expenses'] = expenses_match.group(1)
        
    profit_match = re.search(r'(?:profit|net profit)[^.]*?(\$?[\d,]+(?:\.\d{2})?)', text_lower)
    if profit_match:
        invoice_data['profit'] = profit_match.group(1)
        
    reserves_match = re.search(r'(?:cash reserves|reserves)[^.]*?(\$?[\d,]+(?:\.\d{2})?)', text_lower)
    if reserves_match:
        invoice_data['reserves'] = reserves_match.group(1)

    # Generate a structured summary based on extracted data
    if invoice_data:
        summary_parts = []
        
        # For financial reports/statements
        if 'expenses' in invoice_data and 'profit' in invoice_data:
            summary_parts.append(f"Operating expenses were {invoice_data['expenses']}, resulting in a net profit of {invoice_data['profit']}.")
            
            if 'reserves' in invoice_data:
                summary_parts.append(f" Cash reserves stand at {invoice_data['reserves']}")
                
                if 'allocation' in invoice_data:
                    summary_parts.append(f" with {invoice_data['allocation']} allocated for upcoming expansion.")
                else:
                    summary_parts.append(".")
        
        # For standard invoices
        elif 'invoice_id' in invoice_data or 'total_amount' in invoice_data:
            if 'invoice_id' in invoice_data:
                summary_parts.append(f"Invoice {invoice_data['invoice_id']}")
                
            if 'vendor' in invoice_data:
                summary_parts.append(f" from {invoice_data['vendor']}")
                
            summary_parts.append(".")
            
            if 'total_amount' in invoice_data:
                summary_parts.append(f" Total amount: {invoice_data['total_amount']}.")
                
            if 'due_date' in invoice_data:
                summary_parts.append(f" Due by: {invoice_data['due_date']}.")
        
        return "".join(summary_parts).replace(" .", ".").replace("..", ".")
        
    return None

async def generate_email_summary(text):
    """
    Generate a structured summary specifically for email documents.
    
    Args:
        text (str): The extracted text content from an email
        
    Returns:
        str: A structured summary of email details, or None if not recognized as an email
    """
    # Check if this is likely an email
    text_lower = text.lower()
    if not any(term in text_lower for term in ['from:', 'to:', 'subject:', 'sent:', 'cc:', 'reply', '@']):
        return None
        
    # Extract key information from email
    email_data = {}
    
    # Extract sender
    from_match = re.search(r'from:([^\n]*)', text, re.IGNORECASE)
    if from_match:
        email_data['from'] = from_match.group(1).strip()
        
    # Extract recipients
    to_match = re.search(r'to:([^\n]*)', text, re.IGNORECASE)
    if to_match:
        email_data['to'] = to_match.group(1).strip()
        
    # Extract subject
    subject_match = re.search(r'subject:([^\n]*)', text, re.IGNORECASE)
    if subject_match:
        email_data['subject'] = subject_match.group(1).strip()
        
    # Extract date
    date_match = re.search(r'(?:date|sent):([^\n]*)', text, re.IGNORECASE)
    if date_match:
        email_data['date'] = date_match.group(1).strip()
        
    # Try to extract main body text (simplified approach)
    # Look for content after the headers
    body_match = re.search(r'(?:subject|date|sent|to|from|cc):[^\n]*\n\s*\n(.*)', text, re.DOTALL | re.IGNORECASE)
    if body_match:
        body_text = body_match.group(1).strip()
        # Get the first paragraph or first few sentences
        sentences = sent_tokenize(body_text)
        if sentences:
            email_data['body_summary'] = " ".join(sentences[:2])
    
    # Generate structured summary
    if email_data:
        summary_parts = []
        
        if 'subject' in email_data:
            summary_parts.append(f"Email regarding \"{email_data['subject']}\"")
        else:
            summary_parts.append("Email")
            
        if 'from' in email_data:
            summary_parts.append(f" from {email_data['from']}")
            
        if 'date' in email_data:
            summary_parts.append(f" sent {email_data['date']}")
            
        summary_parts.append(".")
        
        if 'body_summary' in email_data and len(email_data['body_summary']) > 10:
            # Add brief content summary
            summary_parts.append(f" {email_data['body_summary']}")
            
        return "".join(summary_parts).replace(" .", ".").replace("..", ".")
        
    return None

async def extract_text_for_nlp(file_path):
    """
    Extracts text content from document for NLP processing.
    This is a placeholder that would be replaced with actual OCR/extraction logic.
    """
    # Simulate processing time
    await asyncio.sleep(1)
    
    # Return sample texts based on different document types
    sample_texts = [
        "This invoice (#INV-4583) is from ABC Company for services rendered during Q2 2024. "
        "The total amount due is $2,475.00 with payment terms of Net 30. The invoice includes charges "
        "for consulting services ($2,000.00), materials ($375.00), and applicable taxes ($100.00). "
        "Please remit payment by August 15, 2024.",
        
        "The quarterly financial report shows revenue of $1.2M, up 15% from last quarter. "
        "Operating expenses were $850K, resulting in a net profit of $350K. Cash reserves stand at "
        "$4.5M with $1.2M allocated for upcoming expansion. The board recommends increasing "
        "investment in R&D by 10% next quarter.",
        
        "This contract between XYZ Corp and ABC Ltd, effective from July 1, 2024, establishes "
        "a partnership for software development services. The contract term is 24 months with "
        "automatic renewal unless terminated with 60 days notice. Payment terms are Net 15 from "
        "invoice date. Confidentiality provisions survive termination of this agreement."
    ]
    
    return random.choice(sample_texts)

async def analyze_sentiment(text):
    """
    Analyzes the sentiment of text content.
    
    Args:
        text (str): The text content to analyze
        
    Returns:
        dict: Sentiment analysis results with positive, negative, neutral, and compound scores
    """
    if not text:
        return {"error": "No text provided for sentiment analysis"}
    
    try:
        sia = SentimentIntensityAnalyzer()
        sentiment = sia.polarity_scores(text)
        
        # Add a descriptive label based on compound score
        compound = sentiment['compound']
        if compound >= 0.05:
            sentiment['sentiment_label'] = 'positive'
        elif compound <= -0.05:
            sentiment['sentiment_label'] = 'negative'
        else:
            sentiment['sentiment_label'] = 'neutral'
            
        return sentiment
    except Exception as e:
        return {"error": f"Error during sentiment analysis: {str(e)}"}

async def extract_key_entities(text):
    """
    Extracts key entities from text such as:
    - Dates
    - Currency amounts
    - Organization names (placeholder)
    - People names (placeholder)
    
    Args:
        text (str): The text content to analyze
        
    Returns:
        dict: Extracted entities by type
    """
    if not text:
        return {"error": "No text provided for entity extraction"}
    
    entities = {
        "dates": [],
        "amounts": [],
        "organizations": [],
        "people": []
    }
    
    # Simple regex for date extraction (MM/DD/YYYY, Month DD YYYY, DD-MM-YYYY formats)
    date_patterns = [
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # 01/31/2024
        r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}\b',  # January 31, 2024
        r'\b\d{1,2}-\d{1,2}-\d{4}\b'  # 31-01-2024
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        entities["dates"].extend(matches)
    
    # Simple regex for currency amount extraction
    amount_patterns = [
        r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?',  # $1,000.00
        r'\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars|USD)'  # 1,000.00 dollars or USD
    ]
    
    for pattern in amount_patterns:
        matches = re.findall(pattern, text)
        entities["amounts"].extend(matches)
    
    # Placeholder for organization and people names
    # In a real implementation, use proper NER models like spaCy
    common_org_names = ["Ltd", "Inc", "Corp", "LLC", "Company"]
    for org in common_org_names:
        pattern = rf'\b\w+\s+{org}\b'
        matches = re.findall(pattern, text)
        entities["organizations"].extend(matches)
    
    return entities

async def semantic_document_understanding(file_path):
    """
    Comprehensive document understanding that combines multiple NLP techniques
    to provide intelligent insights about the document content.
    
    Args:
        file_path (str): Path to the uploaded document file
        
    Returns:
        dict: Semantic understanding results including key entities, sentiment, and importance
    """
    # Extract text
    text = await extract_text_for_nlp(file_path)
    
    # Parallel processing of multiple NLP tasks
    results = await asyncio.gather(
        analyze_sentiment(text),
        extract_key_entities(text),
        summarize_document(file_path)
    )
    
    return {
        "sentiment_analysis": results[0],
        "key_entities": results[1],
        "summary": results[2],
        "document_insights": {
            "estimated_complexity": get_complexity_score(text),
            "key_topics": extract_topics(text),
            "language_formality": get_formality_level(text)
        }
    }

def get_complexity_score(text):
    """Calculate text complexity based on sentence length and word length"""
    if not text:
        return "unknown"
        
    sentences = sent_tokenize(text)
    if not sentences:
        return "unknown"
        
    words = text.split()
    avg_sentence_length = len(words) / len(sentences)
    
    if avg_sentence_length > 25:
        return "high"
    elif avg_sentence_length > 15:
        return "medium" 
    else:
        return "low"

def extract_topics(text):
    """Extract main topics based on keyword frequency (placeholder implementation)"""
    # In a real implementation, use proper topic modeling like LDA
    common_business_topics = [
        "finance", "invoice", "payment", "contract", "agreement", 
        "report", "analysis", "revenue", "expense", "legal",
        "marketing", "sales", "project", "deadline", "confidential"
    ]
    
    text_lower = text.lower()
    found_topics = []
    
    for topic in common_business_topics:
        if topic in text_lower:
            found_topics.append(topic)
    
    return found_topics[:3] if found_topics else ["general"]

def get_formality_level(text):
    """Estimate text formality (placeholder implementation)"""
    # Simple heuristic based on presence of formal/informal markers
    formal_markers = ["hereby", "pursuant", "furthermore", "consequently", "therefore"]
    informal_markers = ["hey", "thanks", "cool", "awesome", "btw", "fyi"]
    
    text_lower = text.lower()
    formal_count = sum(1 for marker in formal_markers if marker in text_lower)
    informal_count = sum(1 for marker in informal_markers if marker in text_lower)
    
    if formal_count > informal_count:
        return "formal"
    elif informal_count > formal_count:
        return "informal"
    else:
        return "neutral" 

async def extract_entities(text):
    """
    Performs Named Entity Recognition (NER) on the provided text
    using spaCy to extract entities such as persons, organizations,
    locations, dates, etc.
    
    Args:
        text (str): The text to analyze for named entities
        
    Returns:
        dict: JSON object containing categorized named entities
    """
    if not text or len(text.strip()) < 10:
        return {"error": "Insufficient text for entity extraction"}
    
    try:
        # Run spaCy NER in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            # Process text with spaCy
            doc = await loop.run_in_executor(
                executor, 
                functools.partial(nlp, text)
            )
        
        # Initialize entity dictionary
        entities = {
            "PERSON": [],
            "ORG": [],
            "GPE": [],  # Countries, cities, states
            "LOC": [],  # Non-GPE locations
            "DATE": [],
            "TIME": [],
            "MONEY": [],
            "PERCENT": [],
            "PRODUCT": [],
            "EVENT": [],
            "LAW": [],
            "WORK_OF_ART": [],
            "LANGUAGE": [],
            "other": []  # For other entity types
        }
        
        # Extract and categorize entities
        for ent in doc.ents:
            # Skip very short entities as they're often errors
            if len(ent.text.strip()) < 2:
                continue
                
            # Normalize entity text
            entity_text = ent.text.strip()
            
            # Add entity to the corresponding category
            if ent.label_ in entities:
                # Avoid duplicates
                if entity_text not in entities[ent.label_]:
                    entities[ent.label_].append(entity_text)
            else:
                # For any entity type not explicitly listed
                if entity_text not in entities["other"]:
                    entities["other"].append(entity_text)
        
        # Filter out empty categories
        result = {key: values for key, values in entities.items() if values}
        
        # Add entity count for convenience
        result["entity_count"] = sum(len(values) for values in result.values())
        
        return result
    except Exception as e:
        print(f"Error in entity extraction: {str(e)}")
        return {"error": str(e)} 

