import uuid
from django.db import models

# Create your models here.

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to='documents/')
    status = models.CharField(max_length=20, choices=[('processing', 'Processing'), ('processed', 'Processed'), ('error', 'Error')], default='processing')
    document_type = models.CharField(max_length=50, null=True, blank=True)
    detected_language = models.CharField(max_length=10, null=True, blank=True)
    extracted_data = models.JSONField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename

class Workflow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class WorkflowStep(models.Model):
    workflow = models.ForeignKey(Workflow, related_name='steps', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    step_order = models.PositiveIntegerField()

    class Meta:
        ordering = ['step_order']

    def __str__(self):
        return f"{self.workflow.name} - Step {self.step_order}: {self.name}"
