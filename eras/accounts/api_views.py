from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Count, Avg
from .models import CitizenProfile, ServiceProviderProfile, BloodRequest
from disasters.models import Disaster, DisasterAlert
from disasters.serializers import DisasterSerializer
from .serializers import (
    UserSerializer, CitizenProfileSerializer, 
    ServiceProviderProfileSerializer, BloodRequestSerializer,
    RegistrationSerializer
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

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_register(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            user_data = UserSerializer(user).data
            return Response({
                'token': token.key,
                'user': user_data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def api_update_profile(request):
    user = request.user
    if user.user_type == 'citizen':
        try:
            profile = user.citizen_profile
            serializer = CitizenProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except CitizenProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)
            
    elif user.user_type == 'service_provider':
        try:
            profile = user.service_provider_profile
            serializer = ServiceProviderProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except ServiceProviderProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)
    return Response({'error': 'Invalid user type'}, status=400)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_dashboard(request):
    user = request.user
    data = {}
    
    if user.user_type == 'citizen':
        try:
            profile = user.citizen_profile
            user_disasters = Disaster.objects.filter(reporter=user)
            data['disaster_stats'] = {
                'total': user_disasters.count(),
                'pending': user_disasters.filter(status='pending').count(),
                'approved': user_disasters.filter(status='approved').count(),
            }
            
            user_blood_requests = BloodRequest.objects.filter(created_by=user)
            data['blood_stats'] = {
                'total_requests': user_blood_requests.count(),
                'open_requests': user_blood_requests.filter(status='open').count(),
            }
            data['profile_complete'] = profile.is_profile_complete()
            
            recent_disasters = Disaster.objects.filter(status='approved').order_by('-created_at')[:5]
            data['recent_disasters'] = DisasterSerializer(recent_disasters, many=True).data
            
        except Exception as e:
            data['error'] = str(e)

    elif user.user_type == 'service_provider':
        try:
            profile = user.service_provider_profile
            data['capacity_percentage'] = profile.get_capacity_percentage()
            data['avg_rating'] = profile.ratings.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
            
            disaster_stats = {
                'reported': Disaster.objects.filter(reporter=user).count(),
                'responded_to': profile.disaster_responses.count(),
            }
            data['disaster_stats'] = disaster_stats
            
            recent_disasters = Disaster.objects.filter(status='approved').order_by('-created_at')[:5]
            data['recent_disasters'] = DisasterSerializer(recent_disasters, many=True).data
            data['profile_complete'] = profile.is_profile_complete()
        except Exception as e:
            data['error'] = str(e)
            
    return Response(data)

class BloodRequestViewSet(viewsets.ModelViewSet):
    queryset = BloodRequest.objects.all().order_by('-id')
    serializer_class = BloodRequestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_search_donors(request):
    blood_group = request.query_params.get('blood_group')
    city = request.query_params.get('city')
    
    donors = CitizenProfile.objects.filter(available_to_donate='yes')
    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    if city:
        donors = donors.filter(city__icontains=city)
        
    serializer = CitizenProfileSerializer(donors, many=True)
    return Response(serializer.data)

class ServiceProviderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceProviderProfile.objects.all()
    serializer_class = ServiceProviderProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_submit_rating(request, provider_id):
    try:
        provider = ServiceProviderProfile.objects.get(id=provider_id)
        rating_val = request.data.get('rating')
        review = request.data.get('review', '')
        
        if not rating_val:
            return Response({'error': 'Rating is required'}, status=400)
            
        from .models import ServiceProviderRating
        rating, created = ServiceProviderRating.objects.update_or_create(
            service_provider=provider,
            user=request.user,
            defaults={'rating': rating_val, 'review': review}
        )
        return Response({'success': True})
    except ServiceProviderProfile.DoesNotExist:
        return Response({'error': 'Provider not found'}, status=404)
