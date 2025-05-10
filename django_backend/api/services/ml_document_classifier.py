
import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import logging
from django.conf import settings
from .firebase_integration import firebase_manager

logger = logging.getLogger(__name__)

class DocumentClassifier:
    """
    ML model for classifying document types based on text content
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DocumentClassifier, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.model = None
        self.model_path = os.path.join(settings.BASE_DIR, 'models', 'document_classifier.joblib')
        self.load_model()
        self._initialized = True
    
    def load_model(self):
        """Load the trained model if it exists"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            if os.path.exists(self.model_path):
                logger.info(f"Loading existing model from {self.model_path}")
                self.model = joblib.load(self.model_path)
                return True
            else:
                logger.info("No existing model found. Creating new model.")
                self._create_initial_model()
                return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self._create_initial_model()
            return False
    
    def _create_initial_model(self):
        """Create an initial model with basic capabilities"""
        try:
            # Create a simple pipeline with TF-IDF and Random Forest
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ('clf', RandomForestClassifier(n_estimators=100))
            ])
            
            # Train on a very small sample dataset (this would normally come from Firebase)
            sample_data = [
                ("Invoice #1234 from Company ABC Total: $500.00", "Invoice"),
                ("Quarterly Financial Report Q3 2023 Revenue: $1.2M", "Financial Report"),
                ("Contract between Party A and Party B", "Contract"),
                ("Receipt for purchase on 01/01/2023", "Receipt")
            ]
            
            X = [text for text, _ in sample_data]
            y = [label for _, label in sample_data]
            
            self.model.fit(X, y)
            
            # Save the initial model
            joblib.dump(self.model, self.model_path)
            logger.info("Created and saved initial model")
        except Exception as e:
            logger.error(f"Error creating initial model: {e}")
            self.model = None
    
    def predict_document_type(self, text):
        """Predict document type from text"""
        if not self.model:
            logger.warning("Model not loaded. Using fallback classification.")
            return self._fallback_classification(text)
        
        try:
            # Predict document type
            doc_type = self.model.predict([text])[0]
            
            # Get prediction probabilities
            probas = self.model.predict_proba([text])[0]
            max_proba = max(probas) * 100
            
            return {
                "documentType": doc_type,
                "confidence": max_proba
            }
        except Exception as e:
            logger.error(f"Error predicting document type: {e}")
            return self._fallback_classification(text)
    
    def _fallback_classification(self, text):
        """Fallback method for document classification based on keywords"""
        text_lower = text.lower()
        
        if "invoice" in text_lower or "inv-" in text_lower or "amount due" in text_lower:
            return {"documentType": "Invoice", "confidence": 85}
        elif "report" in text_lower or "quarterly" in text_lower or "revenue" in text_lower:
            return {"documentType": "Financial Report", "confidence": 80}
        elif "contract" in text_lower or "agreement" in text_lower:
            return {"documentType": "Contract", "confidence": 75}
        elif "receipt" in text_lower or "payment received" in text_lower:
            return {"documentType": "Receipt", "confidence": 70}
        else:
            return {"documentType": "General Document", "confidence": 60}
    
    def update_model(self, force_train=False):
        """Retrain the model with new data from Firebase"""
        if not firebase_manager.is_initialized():
            logger.warning("Firebase not initialized. Can't update model.")
            return False
        
        try:
            # Get training data from Firebase
            training_data = firebase_manager.get_training_dataset(limit=1000)
            
            if not training_data:
                logger.info("No training data available in Firebase")
                return False
            
            # Extract text and document types
            X = [item.get('text', '') for item in training_data if 'text' in item]
            y = [item.get('documentType', 'General Document') for item in training_data if 'documentType' in item]
            
            if len(X) < 10:  # Need minimum amount of data
                logger.info(f"Not enough training samples ({len(X)}). Need at least 10.")
                return False
            
            logger.info(f"Retraining model with {len(X)} samples")
            
            # Split data for training and evaluation
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Create a new pipeline
            new_model = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ('clf', RandomForestClassifier(n_estimators=100))
            ])
            
            # Train the new model
            new_model.fit(X_train, y_train)
            
            # Evaluate on test set
            y_pred = new_model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"New model accuracy: {accuracy:.4f}")
            
            # If new model is better or force training is requested, replace the old one
            current_accuracy = 0.7  # Default starting point
            if self.model:
                try:
                    current_y_pred = self.model.predict(X_test)
                    current_accuracy = accuracy_score(y_test, current_y_pred)
                except:
                    pass
            
            if force_train or accuracy > current_accuracy:
                logger.info(f"Replacing model (Old: {current_accuracy:.4f}, New: {accuracy:.4f})")
                self.model = new_model
                joblib.dump(self.model, self.model_path)
                return True
            else:
                logger.info(f"Keeping current model (Current: {current_accuracy:.4f}, New: {accuracy:.4f})")
                return False
                
        except Exception as e:
            logger.error(f"Error updating model: {e}")
            return False

# Create an instance of the classifier
document_classifier = DocumentClassifier()
