from rest_framework import serializers
from .models import Document, Workflow, WorkflowStep, ValidationRule


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['id', 'uploaded_at', 'status', 'document_type', 'detected_language', 'extracted_data', 'summary']
        # Make filename read-only because we will set it automatically in the view.
        extra_kwargs = {
            'filename': {'read_only': True}
        } 

class WorkflowStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowStep
        fields = ['id', 'workflow', 'name', 'description', 'step_order']

class WorkflowSerializer(serializers.ModelSerializer):
    steps = WorkflowStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = Workflow
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'steps']
        read_only_fields = ['id', 'created_at']
        
class WorkflowDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed workflow information including steps"""
    steps = WorkflowStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = Workflow
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'steps']

class ValidationRuleSerializer(serializers.ModelSerializer):
    """Serializer for validation rules that users can create and manage"""
    
    class Meta:
        model = ValidationRule
        fields = [
            'id', 'name', 'document_type', 'field_name', 
            'rule_type', 'rule_pattern', 'description', 
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
