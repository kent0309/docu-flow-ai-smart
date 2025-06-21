import asyncio
import random


async def classify_document(file_path):
    """
    Placeholder document classification service.
    
    Args:
        file_path (str): Path to the uploaded document file
        
    Returns:
        str: Classified document type
    """
    # Simulate AI processing time
    await asyncio.sleep(2)
    
    # Return a random document type for demo purposes
    document_types = ['invoice', 'contract', 'receipt', 'report', 'memo', 'letter']
    return random.choice(document_types) 