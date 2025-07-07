from langdetect import detect
import pycountry


def detect_and_get_language_name(text):
    """
    Detects the language of the given text and returns the full language name.
    
    Args:
        text (str): The text to analyze for language detection
        
    Returns:
        str: The full language name (e.g., "English") or "Unknown" if detection fails
    """
    try:
        # Use langdetect to get the two-letter language code
        lang_code = detect(text)
        
        # Use pycountry to look up the full name of the language
        language = pycountry.languages.get(alpha_2=lang_code)
        
        if language:
            return language.name
        else:
            # If pycountry doesn't recognize the code, return the code itself
            return f"Language ({lang_code})"
            
    except Exception:
        # If langdetect or any other operation fails, return "Unknown"
        return "Unknown" 