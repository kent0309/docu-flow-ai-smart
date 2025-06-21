import uuid
from django.db import models

# Create your models here.

class Document(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to='uploads/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    document_type = models.CharField(max_length=50, null=True, blank=True)
    extracted_data = models.JSONField(null=True)
    summary = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.filename} ({self.status})"
    
    class Meta:
        ordering = ['-uploaded_at']
