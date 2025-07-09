from django.contrib import admin
from .models import Document, Workflow, WorkflowStep, ValidationRule, Notification

# Register your models here.

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'status', 'document_type', 'detected_language', 'uploaded_at']
    list_filter = ['status', 'document_type', 'detected_language', 'uploaded_at']
    search_fields = ['filename', 'document_type']
    readonly_fields = ['id', 'uploaded_at']
    ordering = ['-uploaded_at']

class WorkflowStepInline(admin.TabularInline):
    model = WorkflowStep
    extra = 1
    ordering = ['step_order']

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at']
    inlines = [WorkflowStepInline]
    ordering = ['-created_at']

@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = ['name', 'workflow', 'step_order']
    list_filter = ['workflow']
    search_fields = ['name', 'description']
    ordering = ['workflow', 'step_order']

@admin.register(ValidationRule)
class ValidationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'document_type', 'field_name', 'rule_type', 'is_active']
    list_filter = ['document_type', 'rule_type', 'is_active', 'created_at']
    search_fields = ['name', 'document_type', 'field_name', 'description']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient_email', 'subject', 'sent_status', 'created_at', 'sent_at']
    list_filter = ['sent_status', 'created_at']
    search_fields = ['recipient_email', 'subject', 'message']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
