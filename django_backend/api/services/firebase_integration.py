
import os
import json
import firebase_admin
from firebase_admin import credentials, storage, firestore
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class FirebaseManager:
    """
    Handles Firebase integration for document storage and dataset management
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        try:
            # Try to initialize Firebase with credentials
            # In production, use environment variables or settings
            cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
            
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
            else:
                # For development, use a JSON string in settings
                cred_json = getattr(settings, 'FIREBASE_CREDENTIALS_JSON', None)
                if cred_json:
                    cred_dict = json.loads(cred_json)
                    cred = credentials.Certificate(cred_dict)
                else:
                    logger.warning("Firebase credentials not found. Some features may not work.")
                    self._initialized = False
                    return
                    
            firebase_admin.initialize_app(cred, {
                'storageBucket': getattr(settings, 'FIREBASE_STORAGE_BUCKET', ''),
                'projectId': getattr(settings, 'FIREBASE_PROJECT_ID', '')
            })
            
            self.bucket = storage.bucket()
            self.db = firestore.client()
            self._initialized = True
            logger.info("Firebase integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            self._initialized = False
    
    def is_initialized(self):
        return self._initialized
    
    def upload_document(self, file_path, destination_path):
        """Upload a document to Firebase Storage"""
        if not self._initialized:
            logger.error("Firebase not initialized. Cannot upload document.")
            return None
            
        try:
            blob = self.bucket.blob(destination_path)
            blob.upload_from_filename(file_path)
            blob.make_public()
            
            # Return the public URL
            return blob.public_url
        except Exception as e:
            logger.error(f"Error uploading document to Firebase: {e}")
            return None
    
    def store_document_metadata(self, document_id, metadata):
        """Store document metadata in Firestore"""
        if not self._initialized:
            logger.error("Firebase not initialized. Cannot store metadata.")
            return False
            
        try:
            doc_ref = self.db.collection('documents').document(str(document_id))
            doc_ref.set(metadata)
            return True
        except Exception as e:
            logger.error(f"Error storing document metadata: {e}")
            return False
    
    def store_processing_result(self, document_id, result_data, doc_type):
        """Store processing results in Firestore for ML training"""
        if not self._initialized:
            logger.error("Firebase not initialized. Cannot store processing result.")
            return False
            
        try:
            # Store in a collection that can be used for training
            training_ref = self.db.collection('training_data').document(str(document_id))
            
            # Add document type for training purposes
            result_data['documentType'] = doc_type
            result_data['timestamp'] = firestore.SERVER_TIMESTAMP
            
            training_ref.set(result_data)
            return True
        except Exception as e:
            logger.error(f"Error storing processing result: {e}")
            return False
    
    def get_training_dataset(self, limit=100):
        """Retrieve dataset for training"""
        if not self._initialized:
            logger.error("Firebase not initialized. Cannot retrieve training data.")
            return []
            
        try:
            docs = self.db.collection('training_data').limit(limit).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.error(f"Error retrieving training data: {e}")
            return []

# Initialize the manager
firebase_manager = FirebaseManager()
