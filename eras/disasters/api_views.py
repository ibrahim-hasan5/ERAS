from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Disaster, DisasterAlert, DisasterResponse, DisasterUpdate
from .serializers import DisasterSerializer, DisasterAlertSerializer, DisasterResponseSerializer, DisasterUpdateSerializer

class DisasterViewSet(viewsets.ModelViewSet):
    queryset = Disaster.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = DisasterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user, status='pending')

class DisasterAlertViewSet(viewsets.ModelViewSet):
    serializer_class = DisasterAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DisasterAlert.objects.filter(user=self.request.user).order_by('-sent_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        alert = self.get_object()
        alert.is_read = True
        from django.utils import timezone
        alert.read_at = timezone.now()
        alert.save()
        return Response({'status': 'alert marked as read'})

class DisasterResponseViewSet(viewsets.ModelViewSet):
    serializer_class = DisasterResponseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        disaster_id = self.request.query_params.get('disaster')
        if disaster_id:
            return DisasterResponse.objects.filter(disaster_id=disaster_id).order_by('-created_at')
        return DisasterResponse.objects.all()

    def perform_create(self, serializer):
        # Ensure user is a service provider
        if self.request.user.user_type != 'service_provider':
             raise serializers.ValidationError("Only service providers can respond to disasters.")
        
        from accounts.models import ServiceProviderProfile
        profile = ServiceProviderProfile.objects.get(user=self.request.user)
        serializer.save(service_provider=profile)

class DisasterUpdateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DisasterUpdateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        disaster_id = self.request.query_params.get('disaster')
        if disaster_id:
            return DisasterUpdate.objects.filter(disaster_id=disaster_id).order_by('-created_at')
        return DisasterUpdate.objects.all()
