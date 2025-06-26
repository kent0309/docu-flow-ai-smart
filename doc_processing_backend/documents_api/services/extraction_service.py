import asyncio
import random


async def extract_data(file_path):
    """
    Placeholder data extraction service.
    
    Args:
        file_path (str): Path to the uploaded document file
        
    Returns:
        dict: Extracted structured data from the document
    """
    # Simulate AI processing time
    await asyncio.sleep(5)
    
    # Return sample structured data
    sample_data = {
        'invoice_id': f'INV-{random.randint(1000, 9999)}',
        'total': round(random.uniform(10.0, 1000.0), 2),
        'date': '2024-01-15',
        'vendor': 'Sample Vendor Inc.',
        'items': [
            {
                'description': 'Sample Product',
                'quantity': random.randint(1, 10),
                'unit_price': round(random.uniform(5.0, 100.0), 2)
            }
        ],
        'confidence_score': round(random.uniform(0.85, 0.99), 2)
    }
    
    return sample_data


async def extract_data_from_document(file_path):
    """
    Placeholder text extraction service for document classification.
    
    Args:
        file_path (str): Path to the uploaded document file
        
    Returns:
        str: Extracted raw text from the document
    """
    # Simulate AI processing time
    await asyncio.sleep(2)
    
    # Return sample text content based on different document types
    sample_texts = [
        'Invoice Number: INV-12345, Amount Due: $750.00, Vendor: Tech Solutions Inc.',
        'Receipt for your purchase at Downtown Coffee Shop. Total: $8.25. Paid with credit card.',
        'The research study demonstrates significant findings in machine learning applications.',
        'Limited time offer! Save 30% on all electronics. Visit our store today!',
        'Dear Team, Please review the attached quarterly report before the meeting.',
        'Application Form - Please complete all sections. Name, Address, Phone Number required.',
        'Dear Hiring Manager, I am writing in response to the job posting for Software Developer.',
        'John Smith - Experienced Software Engineer with expertise in Python, Django, and cloud computing.'
    ]
    
    return random.choice(sample_texts) 