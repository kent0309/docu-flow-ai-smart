
from django.contrib import admin
from .models import Document, ProcessedDocument

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'file_type', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('title',)

@admin.register(ProcessedDocument)
class ProcessedDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'status', 'processed_at')
    list_filter = ('status', 'processed_at')
    search_fields = ('document__title',)
