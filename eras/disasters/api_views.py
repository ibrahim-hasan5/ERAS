from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Disaster, DisasterAlert
from .serializers import DisasterSerializer, DisasterAlertSerializer

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
