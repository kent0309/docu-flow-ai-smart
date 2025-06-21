from django.contrib import admin
from .models import Document

# Register your models here.

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'status', 'document_type', 'uploaded_at']
    list_filter = ['status', 'document_type', 'uploaded_at']
    search_fields = ['filename', 'document_type']
    readonly_fields = ['id', 'uploaded_at']
    ordering = ['-uploaded_at']
