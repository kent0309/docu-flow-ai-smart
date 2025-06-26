import joblib
import os
from langdetect import detect, LangDetectException

model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml_models', 'document_classifier_pipeline.joblib')
try:
    classifier_pipeline = joblib.load(model_path)
    print(f"Classification model loaded successfully from {model_path}")
except FileNotFoundError:
    print(f"WARNING: Classification model not found at {model_path}. Please run the training script.")
    classifier_pipeline = None

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