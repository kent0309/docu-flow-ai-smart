from django.db import models
import uuid

class Document(models.Model):
    class Status(models.TextChoices):
        PROCESSING = 'processing', 'Processing'
        PROCESSED = 'processed', 'Processed'
        ERROR = 'error', 'Error'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='documents/')
    filename = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROCESSING)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    confidence = models.FloatField(blank=True, null=True)
    extracted_data = models.JSONField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.filename
