import asyncio
import random
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import io
import math
from dateutil import parser as date_parser

# Import for PDF extraction
import pdfplumber

# Import for image-based extraction
try:
    import cv2
    import pytesseract
    import numpy as np
    from PIL import Image
    HAS_OCR_SUPPORT = True
    
    # Set Tesseract executable path for Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except ImportError:
    HAS_OCR_SUPPORT = False

# Import for LLM integration
import google.generativeai as genai

# Type definitions for better type hinting
DocumentData = Dict[str, Any]
ValidationResult = Dict[str, Any]

class DataExtractionError(Exception):
    """Custom exception for extraction errors"""
    pass

# File type handlers
async def extract_data(file_path: str) -> DocumentData:
    """
    Main extraction function that processes documents based on file type.
    
    Args:
        file_path (str): Path to the uploaded document file
        
    Returns:
        dict: Extracted structured data from the document
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise DataExtractionError(f"File not found: {file_path}")
    
    # First extract the text content from the document
    extracted_text = await extract_data_from_document(file_path)
    
    if not extracted_text:
        return {"error": "Failed to extract text from document"}
    
    # Process the extracted text with the LLM
    try:
        llm_results = await process_document_with_llm(extracted_text)
        
        # Add metadata and extraction time
        llm_results["extraction_time"] = datetime.now().isoformat()
        llm_results["file_type"] = os.path.splitext(file_path)[1][1:] if os.path.splitext(file_path)[1] else "unknown"
        llm_results["raw_text"] = extracted_text
        
        return llm_results
    except Exception as e:
        print(f"Error processing with LLM: {str(e)}")
        
        # Fallback to the old extraction method
        file_extension = os.path.splitext(file_path)[1].lower()
        
        extracted_data = {}
        
        try:
            if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                _, extracted_data = await extract_from_image(file_path)
            elif file_extension == '.pdf':
                _, extracted_data = await extract_from_pdf(file_path)
            elif file_extension in ['.txt', '.csv', '.json', '.xml']:
                _, extracted_data = await extract_from_text_file(file_path, file_extension)
            else:
                # For unsupported types, use empty data
                extracted_data = {"error": "Unsupported file type"}
        except Exception as e:
            print(f"Extraction error: {str(e)}")
            extracted_data = {"error": str(e)}
        
        # Add raw text to the extracted data
        extracted_data["raw_text"] = extracted_text
        
        # Add metadata and validate extraction
        extracted_data["extraction_time"] = datetime.now().isoformat()
        extracted_data["file_type"] = file_extension[1:] if file_extension else "unknown"  # Remove leading dot
        
        # Validate the extracted data
        validation_result = validate_extracted_data(extracted_data)
        extracted_data["validation_result"] = validation_result
        
        # Calculate confidence score based on validation and extraction quality
        confidence_factor = 0.8 if validation_result["valid"] else 0.4
        
        # Adjust confidence calculation based on document type
        if "document_subtype" in extracted_data and extracted_data["document_subtype"] == "email":
            # For emails, check for email-specific fields
            email_fields = ['from', 'to', 'subject', 'date']
            email_quality = sum(1 for field in email_fields if field in extracted_data) / len(email_fields)
            extraction_quality = max(0.5, email_quality)
        else:
            # For other documents, use standard confidence calculation
            extraction_quality = 0.9 if all(key in extracted_data for key in ["invoice_id", "date", "total"]) else 0.5
        
        confidence = extraction_quality * confidence_factor
        extracted_data["confidence_score"] = round(confidence, 2)
        
        return extracted_data

async def extract_from_image(file_path: str) -> Tuple[str, DocumentData]:
    """
    Extract data from image files using OCR
    
    Args:
        file_path (str): Path to the image file
        
    Returns:
        Tuple[str, Dict]: The extracted text and structured data
    """
    if not HAS_OCR_SUPPORT:
        return "", {"error": "OCR support not available. Install cv2 and pytesseract."}
        
    try:
        # Read the image using OpenCV
        image = cv2.imread(file_path)
        if image is None:
            return "", {"error": "Failed to read image file"}
            
        # Convert to grayscale for better OCR
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to improve OCR accuracy
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # Use pytesseract to extract text
        extracted_text = pytesseract.image_to_string(gray)
        
        if not extracted_text.strip():
            return "", {"error": "No text could be extracted from the image"}
            
        # Extract structured data from the text
        data = {}
        
        # Extract key information using helper functions
        invoice_id = extract_invoice_id(extracted_text)
        if invoice_id:
            data["invoice_id"] = invoice_id
            
        amount = extract_amount(extracted_text)
        if amount is not None:
            data["total"] = amount
            
        date = extract_date(extracted_text)
        if date:
            data["date"] = date
            
        vendor = extract_vendor_name(extracted_text)
        if vendor:
            data["vendor"] = vendor
            
        # Try to extract line items
        items = extract_line_items(extracted_text)
        if items:
            data["items"] = items
            
        return extracted_text, data
        
    except Exception as e:
        print(f"Error in image extraction: {e}")
        return "", {"error": f"Image processing error: {str(e)}"}

async def extract_from_pdf(file_path: str) -> Tuple[str, DocumentData]:
    """
    Extract data from PDF files using pdfplumber
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        Tuple[str, Dict]: The extracted text and structured data
    """
    try:
        all_text = []
        data = {}
        
        # Open the PDF with pdfplumber
        with pdfplumber.open(file_path) as pdf:
            # Extract text from all pages
            for page in pdf.pages:
                text = page.extract_text() or ""
                all_text.append(text)
                
        # Combine all extracted text
        extracted_text = "\n".join(all_text)
        
        if not extracted_text.strip():
            return "", {"error": "No text could be extracted from the PDF"}
            
        # Extract key information using helper functions
        invoice_id = extract_invoice_id(extracted_text)
        if invoice_id:
            data["invoice_id"] = invoice_id
            
        amount = extract_amount(extracted_text)
        if amount is not None:
            data["total"] = amount
            
        date = extract_date(extracted_text)
        if date:
            data["date"] = date
            
        vendor = extract_vendor_name(extracted_text)
        if vendor:
            data["vendor"] = vendor
            
        # Try to extract line items
        items = extract_line_items(extracted_text)
        if items:
            data["items"] = items
            
        return extracted_text, data
        
    except Exception as e:
        print(f"Error in PDF extraction: {e}")
        return "", {"error": f"PDF processing error: {str(e)}"}

async def extract_from_text_file(file_path: str, extension: str) -> Tuple[str, DocumentData]:
    """
    Extract data from text-based files like TXT, CSV, JSON, XML
    
    Args:
        file_path (str): Path to the text file
        extension (str): File extension
        
    Returns:
        Tuple[str, Dict]: The extracted text and structured data
    """
    try:
        data = {}
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        if extension == '.json':
            # For JSON files, parse the JSON content directly
            try:
                data = json.loads(content)
                return content, data
            except json.JSONDecodeError:
                return content, {"error": "Invalid JSON content"}
                
        elif extension == '.csv':
            # For CSV, we'll return the raw content and extract key-value if possible
            lines = content.strip().split('\n')
            if len(lines) > 1:
                headers = [h.strip() for h in lines[0].split(',')]
                values = [v.strip() for v in lines[1].split(',')]
                
                # Create a dictionary from headers and values
                for i, header in enumerate(headers):
                    if i < len(values):
                        data[header] = values[i]
            
        # For all text files, try to extract key information
        invoice_id = extract_invoice_id(content)
        if invoice_id:
            data["invoice_id"] = invoice_id
            
        amount = extract_amount(content)
        if amount is not None:
            data["total"] = amount
            
        date = extract_date(content)
        if date:
            data["date"] = date
            
        vendor = extract_vendor_name(content)
        if vendor:
            data["vendor"] = vendor
            
        return content, data
        
    except UnicodeDecodeError:
        # If UTF-8 fails, try another encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
                return content, {"warning": "File was decoded with latin-1 encoding"}
        except Exception as e:
            return "", {"error": f"Error reading text file: {str(e)}"}
    except Exception as e:
        return "", {"error": f"Error processing text file: {str(e)}"}

def validate_extracted_data(data: DocumentData) -> ValidationResult:
    """
    Validate the extracted data to ensure it meets our requirements
    
    Args:
        data (dict): The extracted data to validate
        
    Returns:
        dict: Validation result with valid flag and any validation errors
    """
    errors = []
    warnings = []
    
    # Basic validation checks for common fields
    if "invoice_id" in data and not data["invoice_id"]:
        errors.append("Invoice ID is empty")
        
    if "total" in data:
        if not isinstance(data["total"], (int, float, str)):
            errors.append("Total amount is not a valid number or string")
        elif isinstance(data["total"], str):
            # Try to convert string to float
            try:
                float(data["total"].replace(',', ''))
            except ValueError:
                errors.append("Total amount is not a valid numeric string")
                
    if "date" in data and not data["date"]:
        errors.append("Date is empty")
        
    if "items" in data and not isinstance(data["items"], list):
        errors.append("Items should be a list")
    
    # Check for minimum required fields based on document type
    if "document_type" in data:
        if data["document_type"] == "invoice":
            if not any(key in data for key in ["invoice_id", "total", "date"]):
                warnings.append("Invoice missing key information (ID, total, or date)")
        elif data["document_type"] == "receipt":
            if not any(key in data for key in ["total", "date"]):
                warnings.append("Receipt missing key information (total or date)")
                
    # Return the validation result
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def extract_invoice_id(text: str) -> Optional[str]:
    """
    Extract invoice ID from text using regex
    
    Args:
        text (str): Text to extract from
        
    Returns:
        str or None: Extracted invoice ID or None if not found
    """
    patterns = [
        r'invoice\s+(?:no|number|#)?\s*[:.\-]?\s*([a-zA-Z0-9\-]+)',
        r'invoice\s+id\s*[:.\-]?\s*([a-zA-Z0-9\-]+)',
        r'bill\s+(?:no|number|#)?\s*[:.\-]?\s*([a-zA-Z0-9\-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
    return None

def extract_amount(text: str) -> Optional[float]:
    """
    Extract total amount from text using regex
    
    Args:
        text (str): Text to extract from
        
    Returns:
        float or None: Extracted amount or None if not found
    """
    patterns = [
        r'total\s*[:.\-]?\s*\$?\s*([\d,]+\.\d{2})',
        r'total\s+amount\s*[:.\-]?\s*\$?\s*([\d,]+\.\d{2})',
        r'amount\s+due\s*[:.\-]?\s*\$?\s*([\d,]+\.\d{2})',
        r'balance\s+due\s*[:.\-]?\s*\$?\s*([\d,]+\.\d{2})',
        r'total\s*[:.\-]?\s*\$?\s*([\d,]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                return float(amount_str)
            except ValueError:
                continue
                
    return None

def extract_date(text: str) -> Optional[str]:
    """
    Extract date from text using regex
    
    Args:
        text (str): Text to extract from
        
    Returns:
        str or None: Extracted date as string or None if not found
    """
    # Pattern to match common date formats (MM/DD/YYYY, DD/MM/YYYY, Month DD, YYYY, etc.)
    patterns = [
        r'(?:date|issued|invoice\s+date)\s*[:.\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(?:date|issued|invoice\s+date)\s*[:.\-]?\s*(\w+\s+\d{1,2},?\s+\d{4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # MM/DD/YYYY or DD/MM/YYYY
        r'(\w+\s+\d{1,2},?\s+\d{4})'  # Month DD, YYYY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
    return None

def extract_vendor_name(text: str) -> Optional[str]:
    """
    Extract vendor name from text using regex
    
    Args:
        text (str): Text to extract from
        
    Returns:
        str or None: Extracted vendor name or None if not found
    """
    # This is a simplified approach; vendor extraction is complex and often requires
    # more sophisticated NLP techniques
    patterns = [
        r'from\s*[:.\-]?\s*([A-Z][A-Za-z\s,]+(?:Inc|LLC|Ltd|Corporation|Corp|Company|Co)\.?)',
        r'vendor\s*[:.\-]?\s*([A-Z][A-Za-z\s,]+(?:Inc|LLC|Ltd|Corporation|Corp|Company|Co)\.?)',
        r'(?:bill|invoice)\s+from\s*[:.\-]?\s*([A-Z][A-Za-z\s,]+(?:Inc|LLC|Ltd|Corporation|Corp|Company|Co)\.?)',
        r'([A-Z][A-Za-z\s,]+(?:Inc|LLC|Ltd|Corporation|Corp|Company|Co)\.?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
            
    return None

def extract_line_items(text: str) -> List[Dict[str, Any]]:
    """
    Extract line items from text (simplified approach)
    
    Args:
        text (str): Text to extract from
        
    Returns:
        list: List of line item dictionaries
    """
    # This is a placeholder for a more sophisticated line item extraction
    # Real implementation would use NLP or pattern recognition to identify tables and item details
    
    # If the text is very short, it's unlikely to have line items
    if len(text) < 100:
        return []
        
    # Try to identify a tabular section with line items
    # This is just a simple heuristic
    lines = text.split('\n')
    items = []
    
    # Look for patterns that indicate line items (quantity, description, price)
    item_pattern = re.compile(r'(\d+)\s+([A-Za-z\s]+)\s+\$?(\d+\.\d{2})')
    
    for line in lines:
        match = item_pattern.search(line)
        if match:
            quantity = int(match.group(1))
            description = match.group(2).strip()
            unit_price = float(match.group(3))
            
            items.append({
                "quantity": quantity,
                "description": description,
                "unit_price": unit_price,
                "total": quantity * unit_price
            })
    
    # If the simple pattern didn't find anything, return an empty list
    return items

def calculate_skew_angle(image):
    """
    Calculate the skew angle of an image.
    
    Args:
        image: The input image
        
    Returns:
        float: The skew angle in degrees, or 0 if no significant skew is detected
    """
    # Convert to grayscale if it's not already
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Threshold the image to get a binary image
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find all contours
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find the largest contour by area - likely to be the document
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get the minimum area rectangle that contains the contour
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[2]
        
        # Adjust the angle
        if angle < -45:
            angle = 90 + angle
            
        return angle
    
    # Return 0 if no significant contours found
    return 0

async def extract_data_from_document(file_path):
    """
    Extract text content from uploaded documents using OCR with sophisticated image preprocessing.
    
    Args:
        file_path (str): Path to the document file
        
    Returns:
        str: The extracted text content or empty string if extraction fails
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return ""
            
        # Determine file type
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Extract text based on file extension
        if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            # For images, use OCR
            if not HAS_OCR_SUPPORT:
                print("Warning: OCR dependencies not installed. Cannot extract text from images.")
                return ""
                
            # Step 1: Load the image using OpenCV
            image = cv2.imread(file_path)
            if image is None:
                print(f"Failed to read image file: {file_path}")
                return ""
            
            # Save original image for potential fallback
            original_image = image.copy()
            
            # Step 2: Convert to Grayscale
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Step 3: Apply Bilateral Filter for Noise Reduction
            # This preserves edges while removing noise
            filtered_image = cv2.bilateralFilter(gray_image, 9, 75, 75)
            
            # Step 4: Apply Otsu's Thresholding
            # Automatically finds optimal threshold value for images with non-uniform lighting
            binary_image = cv2.threshold(filtered_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Step 5: Apply morphological operations to clean up the image
            # Create a kernel for morphological operations
            kernel = np.ones((1, 1), np.uint8)
            # Apply morphological operations to clean up the image
            cleaned_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)
            
            # Step 6: Deskew the image (correct rotation)
            skew_angle = calculate_skew_angle(cleaned_image)
            if abs(skew_angle) > 0.5:
                print(f"Correcting image skew of {skew_angle:.2f} degrees")
                (h, w) = cleaned_image.shape[:2]
                center = (w // 2, h // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
                cleaned_image = cv2.warpAffine(
                    cleaned_image, 
                    rotation_matrix, 
                    (w, h), 
                    flags=cv2.INTER_CUBIC, 
                    borderMode=cv2.BORDER_REPLICATE
                )
            
            # Step 7: Try multiple Tesseract configurations and pick the best result
            results = []
            
            # Different PSM modes to try
            psm_modes = [
                "--oem 3 --psm 6",  # Assume single uniform block of text
                "--oem 3 --psm 3",  # Auto-detect page layout
                "--oem 3 --psm 4",  # Single column of text
                "--oem 3 --psm 1"   # Automatic page segmentation with OSD
            ]
            
            # Try different image processing variants
            images_to_try = [
                ("cleaned_binary", cleaned_image),
                ("original_grayscale", gray_image),
                ("bilateral_filtered", filtered_image)
            ]
            
            # Try each combination
            for img_name, img in images_to_try:
                for psm in psm_modes:
                    try:
                        text = pytesseract.image_to_string(img, config=psm)
                        text = text.strip()
                        
                        # Calculate a quality score based on text length and ratio of alphanumeric characters
                        if text:
                            alphanumeric_chars = sum(c.isalnum() for c in text)
                            total_chars = max(1, len(text))  # Avoid division by zero
                            quality_score = (alphanumeric_chars / total_chars) * len(text)
                            
                            results.append({
                                "text": text,
                                "quality_score": quality_score,
                                "method": f"{img_name} with {psm}"
                            })
                            
                            print(f"Method: {img_name} with {psm}")
                            print(f"Quality score: {quality_score}")
                            print(f"Text preview: {text[:100]}...")
                    except Exception as e:
                        print(f"Error with {img_name} and {psm}: {str(e)}")
            
            # If we have results, select the best one
            if results:
                # Sort by quality score
                results.sort(key=lambda x: x["quality_score"], reverse=True)
                best_result = results[0]
                print(f"Selected best OCR result: {best_result['method']} with score {best_result['quality_score']}")
                return best_result["text"]
            
            # Fallback to original image with default settings if all else fails
            print("All processing methods failed, falling back to default OCR on original image")
            return pytesseract.image_to_string(original_image).strip()
            
        elif file_extension == '.pdf':
            # For PDFs, use pdfplumber
            text_content = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    text_content.append(text)
                    
            extracted_text = "\n".join(text_content)
            return extracted_text
            
        elif file_extension in ['.txt', '.csv', '.json', '.xml', '.html']:
            # For text-based files, read the content directly
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
                return extracted_text
            except UnicodeDecodeError:
                # If UTF-8 fails, try another common encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    extracted_text = f.read()
                return extracted_text
        else:
            print(f"Unsupported file type for text extraction: {file_extension}")
            return ""
            
    except Exception as e:
        print(f"Error extracting text from document: {str(e)}")
        return ""

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
            
        # Configure the Google Generative AI library with the API key
        genai.configure(api_key=api_key)
        
        # Create a detailed prompt for the LLM with few-shot examples
        prompt = """
You are a highly intelligent document processing AI. Your sole purpose is to analyze the provided text and return a single, perfectly formatted JSON object. You must not, under any circumstances, provide any explanatory text, apologies, or markdown formatting like ```json before or after the JSON object.

Based on the text below, provide a JSON object with the following structure:
{
  "document_type": "Classify the document into ONE of the following specific categories. Use keywords to help you decide: 
    'Advertisement' (if the primary purpose is to promote a product, and it contains coupons, offers, promotional language, product displays, marketing copy, calls to action, special deals, event announcements, price highlights, or branded content),
    'Form' (if it has fields for signatures, dates, approvals, or information to be filled in, including blank lines, checkboxes, radio buttons, dropdown indicators, submission instructions, or form validation instructions),
    'Email' (if it shows sender/receiver addresses, subject line, message body, email headers, signature block),
    'Letter' (if it contains letterhead, formal greeting, signature, date line, recipient address block),
    'Invoice' (if it shows payment terms, itemized lists with prices, invoice numbers, billing addresses),
    'Receipt' (if it shows transaction records, paid amounts, merchant details, payment confirmation),
    'Contract' (if it contains legal terms, party names, obligations, clauses, termination conditions),
    'Report' (if it contains data analysis, findings, summaries, recommendations),
    'Other' (ONLY use this if the document truly doesn't fit any of the above categories).",
  "detected_language": "The primary language of the document, identified by its two-letter ISO 639-1 code (e.g., 'en' for English, 'es' for Spanish).",
  "summary": "A detailed, multi-sentence summary in a single paragraph that captures the key purpose, main topics, and any critical actions or conclusions mentioned in the document.",
  "sentiment": "Analyze the overall tone of the document and classify it as 'Positive', 'Negative', or 'Neutral'.",
  "extracted_data": {
    "//": "Identify every distinct piece of information, label it with a clear, camelCase key, and extract its value exactly as it appears in the text. This should be a comprehensive extraction of all available data."
  }
}

Here is the document text to analyze:
---
{text_content}
---

CRITICAL REMINDER: Your entire response must be ONLY the JSON object and nothing else.
"""
        
        # Define safety settings to prevent AI safety filters from blocking valid responses
        safety_settings = {
            'HATE_SPEECH': 'BLOCK_NONE',
            'HARASSMENT': 'BLOCK_NONE',
            'SEXUALLY_EXPLICIT': 'BLOCK_NONE',
            'DANGEROUS_CONTENT': 'BLOCK_NONE',
        }
        
        # Initialize the Gemini model with safety settings
        model = genai.GenerativeModel('gemini-1.5-flash-latest', safety_settings=safety_settings)
        
        # Configure generation parameters
        generation_config = {
            "temperature": 0.0,  # Set to 0 for most deterministic, factual response
            "max_output_tokens": 4000,
            "top_p": 1.0,
            "top_k": 40,
            "response_mime_type": "application/json"  # Request JSON response directly
        }
        
        # Call the Gemini API
        response = await asyncio.to_thread(
            model.generate_content,
            prompt,
            generation_config=generation_config
        )
        
        # Log the raw response for debugging
        print("--- RAW LLM RESPONSE ---")
        print(response.text)
        print("--- END RAW LLM RESPONSE ---")
        
        # Extract the response content
        llm_response = response.text
        
        # Check if response looks like a JSON object before parsing
        if not llm_response or not llm_response.strip():
            raise ValueError("Empty response received from LLM")
        
        # Check if the response at least starts and ends with curly braces (basic JSON structure)
        trimmed_response = llm_response.strip()
        if not (trimmed_response.startswith('{') and trimmed_response.endswith('}')):
            print(f"Warning: Response doesn't appear to be a valid JSON object: {trimmed_response[:100]}...")
        
        try:
            # Try parsing the response directly as JSON first
            result = json.loads(llm_response)
            print("Successfully parsed JSON response")
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            # Fall back to regex extraction if direct parsing fails
            # Try to find JSON object in the response (it might be wrapped in markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', llm_response)
            if json_match:
                json_str = json_match.group(1)
                print(f"Extracted JSON from code block: {json_str[:100]}...")
            else:
                json_str = llm_response
                print("No code block found, using raw response")
            
            # Clean up any non-JSON text that might be present
            json_str = re.sub(r'^[^{]*', '', json_str)
            json_str = re.sub(r'[^}]*$', '', json_str)
            
            try:
                result = json.loads(json_str)
                print("Successfully parsed JSON after cleanup")
            except json.JSONDecodeError as nested_e:
                # If JSON parsing fails, try to fix common issues
                print(f"JSON parsing still failed after cleanup: {str(nested_e)}")
                # Remove any trailing commas before closing braces/brackets
                json_str = re.sub(r',(\s*[\]}])', r'\1', json_str)
                print(f"Attempting final cleanup and parse: {json_str[:100]}...")
                try:
                    result = json.loads(json_str)
                    print("Successfully parsed JSON after final cleanup")
                except json.JSONDecodeError as final_e:
                    print(f"All JSON parsing attempts failed: {str(final_e)}")
                    raise ValueError(f"Failed to parse LLM response as JSON: {str(final_e)}")
        
        # Validate the result has the expected structure
        if not all(key in result for key in ['document_type', 'detected_language', 'extracted_data', 'summary']):
            missing_keys = [key for key in ['document_type', 'detected_language', 'extracted_data', 'summary'] if key not in result]
            raise ValueError(f"LLM response missing required keys: {', '.join(missing_keys)}")
            
        # Clean and validate the extracted data
        result = validate_and_clean_data(result)
            
        return result
        
    except Exception as e:
        print(f"Error processing document with LLM: {str(e)}")
        # Return a default structure with the error
        return {
            "document_type": "Unknown",
            "detected_language": "en",  # Default to English
            "extracted_data": {
                "error": {
                    "value": f"Failed to process with LLM: {str(e)}",
                    "confidence": "Low"
                },
                "raw_text": {
                    "value": text_content[:500] + "..." if len(text_content) > 500 else text_content,
                    "confidence": "High"
                }
            },
            "summary": "Document could not be processed automatically due to an error.",
            "confidence_score": 0.1
        }

def process_email_text(extracted_text):
    """
    Process extracted text that appears to be an email to improve structure and readability.
    
    Args:
        extracted_text (str): The raw extracted text from an email document
        
    Returns:
        str: Processed email text with improved formatting
    """
    lines = extracted_text.split('\n')
    processed_lines = []
    
    # States for parsing
    in_header = True
    header_pattern = re.compile(r'^(from|to|cc|bcc|subject|date|sent):', re.IGNORECASE)
    
    for line in lines:
        # Clean up the line
        clean_line = line.strip()
        
        # Skip empty lines in header section
        if in_header and not clean_line:
            continue
            
        # Check if we're still in the header section
        if in_header and not header_pattern.match(clean_line) and len(clean_line) > 0:
            # If this line doesn't look like a header and isn't empty, we've reached the body
            in_header = False
            # Add a separator between header and body
            processed_lines.append("")
            
        # Add the line to processed output
        if clean_line or not in_header:  # Only keep empty lines in the body
            processed_lines.append(clean_line)
            
    return '\n'.join(processed_lines)

def extract_email_metadata(text):
    """
    Extract structured metadata from email text content.
    
    Args:
        text (str): The extracted text content from an email
        
    Returns:
        dict: Structured metadata from the email
    """
    metadata = {}
    
    # Extract common email headers
    headers = {
        'from': re.search(r'from:([^\n]*)', text, re.IGNORECASE),
        'to': re.search(r'to:([^\n]*)', text, re.IGNORECASE),
        'subject': re.search(r'subject:([^\n]*)', text, re.IGNORECASE),
        'date': re.search(r'(?:date|sent):([^\n]*)', text, re.IGNORECASE),
        'cc': re.search(r'cc:([^\n]*)', text, re.IGNORECASE)
    }
    
    # Add found headers to metadata
    for key, match in headers.items():
        if match:
            metadata[key] = match.group(1).strip()
            
    # Extract email addresses
    email_addresses = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email_addresses:
        metadata['email_addresses'] = list(set(email_addresses))  # Remove duplicates
        
    # Try to extract main body
    body_match = re.search(r'(?:subject|date|sent|to|from|cc):[^\n]*\n\s*\n(.*)', text, re.DOTALL | re.IGNORECASE)
    if body_match:
        metadata['body'] = body_match.group(1).strip()
        
    return metadata

def convert_to_format(data: DocumentData, output_format: str) -> str:
    """
    Convert extracted data to specified format (JSON, CSV, or XML)
    
    Args:
        data (dict): The structured data to convert
        output_format (str): The target format ('json', 'csv', or 'xml')
        
    Returns:
        str: The data in the specified format
    """
    output_format = output_format.lower()
    
    if output_format == 'json':
        return json.dumps(data, indent=2)
        
    elif output_format == 'csv':
        # Flatten the data structure
        flat_data = {}
        
        def flatten_dict(d, prefix=''):
            for k, v in d.items():
                if isinstance(v, dict):
                    flatten_dict(v, f"{prefix}{k}_")
                elif isinstance(v, list):
                    # For lists, we'll join the values with a pipe
                    if all(isinstance(i, (str, int, float, bool)) for i in v):
                        flat_data[f"{prefix}{k}"] = "|".join(str(i) for i in v)
                    else:
                        # For lists of objects, we'll create separate columns
                        for i, item in enumerate(v):
                            if isinstance(item, dict):
                                flatten_dict(item, f"{prefix}{k}_{i+1}_")
                else:
                    flat_data[f"{prefix}{k}"] = v
                    
        flatten_dict(data)
        
        # Create CSV
        output = io.StringIO()
        if flat_data:
            headers = flat_data.keys()
            output.write(",".join(headers) + "\n")
            output.write(",".join(str(flat_data[h]) for h in headers))
        return output.getvalue()
        
    elif output_format == 'xml':
        # Simple XML generation
        output = ['<?xml version="1.0" encoding="UTF-8"?>']
        output.append('<document>')
        
        def dict_to_xml(d, parent_tag):
            result = []
            for k, v in d.items():
                if isinstance(v, dict):
                    result.append(f"<{k}>")
                    result.append(dict_to_xml(v, k))
                    result.append(f"</{k}>")
                elif isinstance(v, list):
                    result.append(f"<{k}>")
                    for item in v:
                        if isinstance(item, dict):
                            result.append(f"<item>")
                            result.append(dict_to_xml(item, 'item'))
                            result.append(f"</item>")
                        else:
                            result.append(f"<item>{item}</item>")
                    result.append(f"</{k}>")
                else:
                    if v is not None:
                        result.append(f"<{k}>{v}</{k}>")
                    else:
                        result.append(f"<{k}></{k}>")
            return "\n".join(result)
            
        output.append(dict_to_xml(data, 'document'))
        output.append('</document>')
        return "\n".join(output)
        
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

def validate_and_clean_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and validate data extracted by the LLM.
    
    Args:
        data (dict): The data extracted by the LLM
        
    Returns:
        dict: Cleaned and validated data
    """
    if not data or not isinstance(data, dict):
        return data
        
    # Ensure extracted_data exists and is a dictionary
    if "extracted_data" not in data or not isinstance(data["extracted_data"], dict):
        return data
        
    # Process each field in extracted_data
    for field, value in list(data["extracted_data"].items()):
        # Skip if the value is None or not a dictionary
        if value is None:
            continue
            
        # Handle the new structure with value and confidence
        if isinstance(value, dict) and "value" in value:
            field_value = value["value"]
            
            # Clean string values
            if isinstance(field_value, str):
                # Trim whitespace
                field_value = field_value.strip()
                value["value"] = field_value
                
            # Format dates to YYYY-MM-DD
            if field in ["date", "due_date", "effective_date", "termination_date"] and field_value:
                try:
                    if isinstance(field_value, str):
                        # Parse the date string
                        parsed_date = date_parser.parse(field_value)
                        # Format to YYYY-MM-DD
                        value["value"] = parsed_date.strftime("%Y-%m-%d")
                except Exception as e:
                    print(f"Error parsing date '{field_value}': {str(e)}")
                    # Add validation error flag
                    value["validation_error"] = f"Invalid date format: {str(e)}"
                    
            # Validate invoice/receipt numbers
            if field in ["invoice_number", "receipt_number"] and field_value:
                if isinstance(field_value, str):
                    # Check if it matches common invoice number patterns
                    if not re.match(r'^[A-Za-z0-9\-_]+$', field_value):
                        value["validation_warning"] = "Invoice/receipt number contains unusual characters"
                        
            # Format monetary values as floats
            if field in ["total_amount", "tax_amount"] or "amount" in field:
                try:
                    if isinstance(field_value, str):
                        # Remove currency symbols and commas
                        cleaned_value = re.sub(r'[^\d.]', '', field_value.replace(',', ''))
                        if cleaned_value:
                            value["value"] = float(cleaned_value)
                except Exception as e:
                    print(f"Error converting monetary value '{field_value}': {str(e)}")
                    value["validation_error"] = f"Invalid monetary value: {str(e)}"
        
        # Handle line items which is typically a list
        elif field == "line_items" and isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    # Clean each item in the list
                    for item_field, item_value in list(item.items()):
                        # Handle the new structure with value and confidence
                        if isinstance(item_value, dict) and "value" in item_value:
                            if item_field == "amount" and isinstance(item_value["value"], str):
                                try:
                                    # Remove currency symbols and commas
                                    cleaned_value = re.sub(r'[^\d.]', '', item_value["value"].replace(',', ''))
                                    if cleaned_value:
                                        item_value["value"] = float(cleaned_value)
                                except Exception:
                                    item_value["validation_error"] = "Invalid monetary value"
                        # Handle direct values (old format)
                        elif item_field == "amount" and isinstance(item_value, str):
                            try:
                                # Remove currency symbols and commas
                                cleaned_value = re.sub(r'[^\d.]', '', item_value.replace(',', ''))
                                if cleaned_value:
                                    item[item_field] = float(cleaned_value)
                            except Exception:
                                item["validation_error"] = "Invalid monetary value"
    
    return data 