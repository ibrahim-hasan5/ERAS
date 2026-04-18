from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import CitizenProfile, ServiceProviderProfile, BloodRequest
from .serializers import (
    UserSerializer, CitizenProfileSerializer, 
    ServiceProviderProfileSerializer, BloodRequestSerializer
)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data
        return Response({
            'token': token.key,
            'user': user_data
        })
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_get_profile(request):
    user = request.user
    if user.user_type == 'citizen':
        try:
            profile = user.citizen_profile
            serializer = CitizenProfileSerializer(profile)
            return Response(serializer.data)
        except CitizenProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)
    elif user.user_type == 'service_provider':
        try:
            profile = user.service_provider_profile
            serializer = ServiceProviderProfileSerializer(profile)
            return Response(serializer.data)
        except ServiceProviderProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)
    return Response({'error': 'Invalid user type'}, status=400)

class BloodRequestViewSet(viewsets.ModelViewSet):
    queryset = BloodRequest.objects.all()
    serializer_class = BloodRequestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
