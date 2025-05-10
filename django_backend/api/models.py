
from django.db import models
import uuid
import os

def document_file_path(instance, filename):
    """Generate file path for new document"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('documents', filename)

class Document(models.Model):
    """Document model for storing uploaded files"""
    DOCUMENT_TYPES = (
        ('pdf', 'PDF'),
        ('docx', 'DOCX'),
        ('jpg', 'JPG/JPEG'),
        ('png', 'PNG'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=document_file_path)
    file_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    @property
    def file_name(self):
        return os.path.basename(self.file.name)
    
    def delete(self, *args, **kwargs):
        # Delete file when model is deleted
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

class ProcessedDocument(models.Model):
    """Model for storing processed document results"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='processed')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    processed_at = models.DateTimeField(auto_now=True)
    extracted_data = models.JSONField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Processed {self.document.title}"
