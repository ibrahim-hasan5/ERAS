from rest_framework import viewsets, permissions
from .models import Disaster
from .serializers import DisasterSerializer

class DisasterViewSet(viewsets.ModelViewSet):
    queryset = Disaster.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = DisasterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
