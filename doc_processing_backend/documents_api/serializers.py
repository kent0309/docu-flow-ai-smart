from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        # Make filename read-only because we will set it automatically in the view.
        extra_kwargs = {
            'filename': {'read_only': True}
        } 