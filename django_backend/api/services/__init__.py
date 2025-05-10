
# Import services to make them available when importing the services package
from .document_processor import extract_data, summarize_document, train_ml_model
from .ml_document_classifier import document_classifier
from .firebase_integration import firebase_manager
