from rest_framework import serializers
from .models import Disaster, DisasterImage, DisasterResponse, DisasterAlert

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

class DisasterAlertSerializer(serializers.ModelSerializer):
    disaster_title = serializers.CharField(source='disaster.title', read_only=True)
    disaster_type = serializers.CharField(source='disaster.get_disaster_type_display', read_only=True)
    severity = serializers.CharField(source='disaster.severity', read_only=True)
    location = serializers.SerializerMethodField()

    class Meta:
        model = DisasterAlert
        fields = ['id', 'disaster', 'disaster_title', 'disaster_type', 'severity', 'location', 'match_type', 'sent_at', 'is_read']

    def get_location(self, obj):
        return f"{obj.disaster.city}, {obj.disaster.area_sector}"
