import json
import re
import os
from typing import Dict, Any, Optional

import google.generativeai as genai

async def process_document_with_llm(text_content: str) -> Dict[str, Any]:
    """
    Process document text with a Large Language Model (LLM) to extract structured information.
    
    Args:
        text_content (str): The text content extracted from the document
        
    Returns:
        dict: A structured dictionary containing document_type, extracted_data and summary
    """
    try:
        # Get the API key from environment variable
        api_key = os.environ.get("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
            
        # Configure the Google Generative AI client
        genai.configure(api_key=api_key)
        
        # Create a prompt for the LLM
        prompt = f"""
        You are an expert document analyzer. Your task is to analyze the following document text
        and extract structured information. Please analyze the document and return a valid JSON object
        with the following three keys:
        
        1. document_type: Classify the document and choose from ["Email", "Invoice", "Receipt", "Contract", "Report", "Form", "Advertisement", "Other"]
        
        2. extracted_data: Extract key information from the document as a structured object with key-value pairs.
           The keys should be relevant to the document type. For example:
           - For an email: sender, recipient, subject, date, body
           - For an invoice: invoice_id, date, total_amount, vendor, items
           - For a receipt: receipt_id, date, total_amount, merchant, items
           - For other documents: Extract any relevant key-value pairs you find
        
        3. summary: Write a concise one or two-sentence summary of the document's purpose or main content.
        
        Here is the document text to analyze:
        
        {text_content}
        
        Remember to respond ONLY with a JSON object containing document_type, extracted_data, and summary keys.
        """
        
        # Get Gemini 2.5 Flash model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Call the LLM API
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0,
                max_output_tokens=4000,
                response_mime_type="application/json"  # Request JSON response directly
            )
        )
        
        # Extract the response content
        llm_response = response.text
        
        try:
            # Try parsing the response directly as JSON first
            result = json.loads(llm_response)
        except json.JSONDecodeError:
            # Fall back to regex extraction if direct parsing fails
            # Try to find JSON object in the response (it might be wrapped in markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', llm_response)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = llm_response
            
            # Clean up any non-JSON text that might be present
            json_str = re.sub(r'^[^{]*', '', json_str)
            json_str = re.sub(r'[^}]*$', '', json_str)
            
            result = json.loads(json_str)
        
        # Validate the result has the expected structure
        if not all(key in result for key in ['document_type', 'extracted_data', 'summary']):
            raise ValueError("LLM response missing required keys")
            
        return result
        
    except Exception as e:
        print(f"Error processing document with LLM: {str(e)}")
        # Return a default structure with the error
        return {
            "document_type": "unknown",
            "extracted_data": {
                "error": f"Failed to process with LLM: {str(e)}"
            },
            "summary": "Document could not be processed automatically.",
            "confidence_score": 0.1
        }

def get_llm_availability() -> Dict[str, Any]:
    """
    Check if LLM integration is available by verifying the API key.
    
    Returns:
        dict: Status information about LLM availability
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if api_key:
        return {
            "available": True,
            "provider": "Google Gemini",
            "version": "2.5 Flash",
        }
    else:
        return {
            "available": False,
            "error": "GOOGLE_API_KEY environment variable not set",
            "setup_instructions": "Set the GOOGLE_API_KEY environment variable with your Google API key."
        }

def create_document_prompt(document_type: str, task: str) -> str:
    """
    Create a specialized prompt for a specific document type and task.
    
    Args:
        document_type (str): The type of document (email, invoice, etc.)
        task (str): The task to perform (summarize, extract, analyze)
        
    Returns:
        str: A specialized prompt template
    """
    base_prompt = f"You are an expert at analyzing {document_type} documents. "
    
    if task == "summarize":
        return base_prompt + "Provide a concise summary of the key information in this document."
    elif task == "extract":
        return base_prompt + f"Extract all relevant information from this {document_type} in JSON format."
    elif task == "analyze":
        return base_prompt + f"Analyze this {document_type} and identify any issues, anomalies, or important points."
    else:
        return base_prompt + "Review this document and provide your expert assessment." 