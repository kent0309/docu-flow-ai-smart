from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'document_type', 'status', 'uploaded_at', 'confidence')
    list_filter = ('status', 'document_type')
    search_fields = ('filename', 'document_type')
    readonly_fields = ('id', 'uploaded_at', 'confidence', 'summary', 'extracted_data')
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'filename', 'file', 'document_type', 'status')
        }),
        ('Processing Results', {
            'fields': ('confidence', 'extracted_data', 'summary'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',),
        }),
    ) 