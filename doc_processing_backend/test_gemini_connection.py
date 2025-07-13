import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_gemini_connection():
    """Test connection to Google Gemini 2.5 Flash API"""
    try:
        # Get API key from environment
        api_key = os.environ.get("GOOGLE_API_KEY")
        
        if not api_key:
            print("❌ Error: GOOGLE_API_KEY not found in environment variables")
            print("Make sure you have set it in your .env file")
            return False
            
        # Configure the API
        print("⏳ Configuring Google Generative AI with provided API key...")
        genai.configure(api_key=api_key)
        
        # Initialize Gemini 2.5 Flash model
        print("⏳ Initializing Gemini 2.5 Flash model...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Make a simple test request
        print("⏳ Testing API with a simple request...")
        response = model.generate_content("Hello, please respond with 'API connection successful'")
        
        # Check response
        if response and response.text:
            print(f"✅ API connection successful! Response received:")
            print(f"\n{response.text}\n")
            return True
        else:
            print("❌ Error: Received empty response from API")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Google Gemini API: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Gemini 2.5 Flash API Connection...\n")
    
    result = test_gemini_connection()
    
    if result:
        print("✅ Test completed successfully! The API is working properly.")
        sys.exit(0)
    else:
        print("❌ Test failed. Please check the error messages above.")
        sys.exit(1) 