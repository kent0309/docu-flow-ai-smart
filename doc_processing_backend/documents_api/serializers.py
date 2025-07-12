from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Document, Workflow, WorkflowStep, ValidationRule, Notification,
    IntegrationConfiguration, IntegrationAuditLog, DocumentApproval,
    WorkflowExecution, RealTimeSyncStatus
)


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['id', 'uploaded_at', 'status', 'document_type', 'detected_language', 'extracted_data', 'summary', 'workflow_status', 'current_approver']
        # Make filename read-only because we will set it automatically in the view.
        extra_kwargs = {
            'filename': {'read_only': True}
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class WorkflowStepSerializer(serializers.ModelSerializer):
    approver = UserSerializer(read_only=True)
    
    class Meta:
        model = WorkflowStep
        fields = ['id', 'workflow', 'name', 'description', 'step_order', 'step_type', 
                 'approver', 'approval_group', 'requires_all_approvers', 
                 'integration_system', 'integration_config', 'condition_field',
                 'condition_value', 'condition_operator']

class WorkflowSerializer(serializers.ModelSerializer):
    steps = WorkflowStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = Workflow
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'steps',
                 'requires_approval', 'approval_threshold', 'auto_approve_below_threshold']
        read_only_fields = ['id', 'created_at']
        
class WorkflowDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed workflow information including steps"""
    steps = WorkflowStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = Workflow
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'steps',
                 'requires_approval', 'approval_threshold', 'auto_approve_below_threshold']

class ValidationRuleSerializer(serializers.ModelSerializer):
    """Serializer for validation rules that users can create and manage"""
    
    class Meta:
        model = ValidationRule
        fields = [
            'id', 'name', 'document_type', 'field_name', 
            'rule_type', 'rule_pattern', 'description', 
            'is_active', 'created_at', 'reference_field', 
            'calculation_type', 'tolerance', 'auto_created'
        ]
        read_only_fields = ['id', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for workflow notifications"""
    
    document_filename = serializers.SerializerMethodField()
    workflow_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient_email', 'subject', 'message',
            'sent_status', 'document', 'workflow', 
            'document_filename', 'workflow_name',
            'created_at', 'sent_at'
        ]
        read_only_fields = ['id', 'sent_status', 'created_at', 'sent_at']
        
    def get_document_filename(self, obj):
        return obj.document.filename if obj.document else None
        
    def get_workflow_name(self, obj):
        return obj.workflow.name if obj.workflow else None

# New serializers for integration and advanced routing

class IntegrationConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for integration configuration"""
    
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = IntegrationConfiguration
        fields = [
            'id', 'name', 'integration_type', 'description',
            'endpoint_url', 'api_key', 'username', 'password',
            'config_data', 'supported_document_types',
            'status', 'last_sync', 'sync_frequency',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_sync']
        extra_kwargs = {
            'password': {'write_only': True}  # Don't expose password in responses
        }

class IntegrationAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for integration audit logs"""
    
    integration_name = serializers.SerializerMethodField()
    document_filename = serializers.SerializerMethodField()
    
    class Meta:
        model = IntegrationAuditLog
        fields = [
            'id', 'integration', 'integration_name', 'document', 'document_filename',
            'action', 'status', 'request_data', 'response_data', 'error_message',
            'started_at', 'completed_at', 'duration_ms', 'external_reference_id'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at', 'duration_ms']
        
    def get_integration_name(self, obj):
        return obj.integration.name if obj.integration else None
        
    def get_document_filename(self, obj):
        return obj.document.filename if obj.document else None

class DocumentApprovalSerializer(serializers.ModelSerializer):
    """Serializer for document approvals"""
    
    approver = UserSerializer(read_only=True)
    delegated_to = UserSerializer(read_only=True)
    document_filename = serializers.SerializerMethodField()
    workflow_step_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentApproval
        fields = [
            'id', 'document', 'document_filename', 'workflow_step', 'workflow_step_name',
            'approver', 'status', 'comments', 'assigned_at', 'reviewed_at', 'due_date',
            'delegated_to', 'delegation_reason', 'approval_level'
        ]
        read_only_fields = ['id', 'assigned_at', 'reviewed_at']
        
    def get_document_filename(self, obj):
        return obj.document.filename if obj.document else None
        
    def get_workflow_step_name(self, obj):
        return obj.workflow_step.name if obj.workflow_step else None

class WorkflowExecutionSerializer(serializers.ModelSerializer):
    """Serializer for workflow executions"""
    
    document_filename = serializers.SerializerMethodField()
    workflow_name = serializers.SerializerMethodField()
    current_step_name = serializers.SerializerMethodField()
    started_by = UserSerializer(read_only=True)
    
    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'document', 'document_filename', 'workflow', 'workflow_name',
            'status', 'current_step', 'current_step_name', 'started_at', 'completed_at',
            'started_by', 'execution_data', 'error_log'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']
        
    def get_document_filename(self, obj):
        return obj.document.filename if obj.document else None
        
    def get_workflow_name(self, obj):
        return obj.workflow.name if obj.workflow else None
        
    def get_current_step_name(self, obj):
        return obj.current_step.name if obj.current_step else None

class RealTimeSyncStatusSerializer(serializers.ModelSerializer):
    """Serializer for real-time sync status"""
    
    document_filename = serializers.SerializerMethodField()
    integration_name = serializers.SerializerMethodField()
    
    class Meta:
        model = RealTimeSyncStatus
        fields = [
            'id', 'document', 'document_filename', 'integration', 'integration_name',
            'sync_type', 'last_sync', 'next_sync', 'is_synced', 'sync_error',
            'retry_count', 'max_retries', 'external_id', 'external_status', 'external_data'
        ]
        read_only_fields = ['id', 'last_sync']
        
    def get_document_filename(self, obj):
        return obj.document.filename if obj.document else None
        
    def get_integration_name(self, obj):
        return obj.integration.name if obj.integration else None

# Combined serializers for complex operations

class DocumentWithApprovalsSerializer(serializers.ModelSerializer):
    """Serializer for documents with their approval information"""
    
    approvals = DocumentApprovalSerializer(many=True, read_only=True)
    current_approver = UserSerializer(read_only=True)
    
    class Meta:
        model = Document
        fields = '__all__'

class WorkflowWithExecutionsSerializer(serializers.ModelSerializer):
    """Serializer for workflows with execution history"""
    
    executions = WorkflowExecutionSerializer(many=True, read_only=True)
    steps = WorkflowStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = Workflow
        fields = '__all__'
