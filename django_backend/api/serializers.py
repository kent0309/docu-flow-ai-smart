
from rest_framework import serializers
from .models import Document, ProcessedDocument

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'file_type', 'uploaded_at', 'file_name']
        read_only_fields = ['file_type', 'uploaded_at', 'file_name']
    
    def create(self, validated_data):
        file_obj = validated_data['file']
        file_extension = file_obj.name.split('.')[-1].lower()
        
        # Map file extension to file type
        extension_map = {
            'pdf': 'pdf',
            'docx': 'docx',
            'doc': 'docx',
            'jpg': 'jpg',
            'jpeg': 'jpg',
            'png': 'png',
        }
        
        validated_data['file_type'] = extension_map.get(file_extension, 'other')
        document = Document.objects.create(**validated_data)
        
        # Create a corresponding ProcessedDocument instance
        ProcessedDocument.objects.create(document=document)
        
        return document

class ExtractedFieldSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.CharField()
    confidence = serializers.FloatField()
    is_valid = serializers.BooleanField()

class ProcessedDocumentSerializer(serializers.ModelSerializer):
    document = DocumentSerializer(read_only=True)
    extracted_fields = ExtractedFieldSerializer(many=True, read_only=True, source='extracted_data.fields')
    
    class Meta:
        model = ProcessedDocument
        fields = ['id', 'document', 'status', 'processed_at', 'summary', 'extracted_fields', 'extracted_data']
