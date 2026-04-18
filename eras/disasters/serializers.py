from rest_framework import serializers
from .models import Disaster, DisasterImage, DisasterResponse

class DisasterImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisasterImage
        fields = ['id', 'image', 'caption', 'is_primary', 'uploaded_at']

class DisasterSerializer(serializers.ModelSerializer):
    images = DisasterImageSerializer(many=True, read_only=True)
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    severity_color = serializers.CharField(source='get_severity_color', read_only=True)
    disaster_icon = serializers.CharField(source='get_disaster_icon', read_only=True)

    class Meta:
        model = Disaster
        fields = '__all__'
        read_only_fields = ['reporter', 'status', 'approved_by', 'approved_at', 'resolved_at']

class DisasterResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisasterResponse
        fields = '__all__'
