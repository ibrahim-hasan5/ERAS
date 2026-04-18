from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CitizenProfile, ServiceProviderProfile, BloodRequest

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number']


class CitizenProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CitizenProfile
        fields = '__all__'


class ServiceProviderProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ServiceProviderProfile
        fields = '__all__'


class BloodRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = '__all__'


class RegistrationSerializer(serializers.Serializer):
    user_type = serializers.ChoiceField(choices=['citizen', 'service_provider'])
    password = serializers.CharField(write_only=True)
    
    # Citizen fields
    username = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    
    # Service Provider fields
    organization_name = serializers.CharField(required=False, allow_blank=True)
    service_type = serializers.CharField(required=False, allow_blank=True)
    contact_number = serializers.CharField(required=False, allow_blank=True)
    
    # Shared
    email = serializers.EmailField()

    def validate(self, data):
        if data['user_type'] == 'citizen':
            if not data.get('username') or not data.get('phone_number'):
                raise serializers.ValidationError("Username and phone number are required for citizens.")
            if User.objects.filter(username=data['username']).exists():
                raise serializers.ValidationError("Username already exists.")
        elif data['user_type'] == 'service_provider':
            if not data.get('organization_name') or not data.get('service_type') or not data.get('contact_number'):
                raise serializers.ValidationError("Organization name, service type, and contact number are required.")
            
            # Username is derived from organization_name
            username = data['organization_name'].lower().replace(' ', '_').replace('-', '_')
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError("An organization with this name already exists.")
            
        return data

    def create(self, validated_data):
        user_type = validated_data['user_type']
        
        if user_type == 'citizen':
            user = User(
                username=validated_data['username'],
                email=validated_data['email'],
                phone_number=validated_data['phone_number'],
                user_type='citizen'
            )
            user.set_password(validated_data['password'])
            user.save()
            CitizenProfile.objects.create(user=user)
            return user
            
        elif user_type == 'service_provider':
            username = validated_data['organization_name'].lower().replace(' ', '_').replace('-', '_')
            user = User(
                username=username,
                email=validated_data['email'],
                phone_number=validated_data['contact_number'],
                user_type='service_provider'
            )
            user.set_password(validated_data['password'])
            user.save()
            ServiceProviderProfile.objects.create(
                user=user,
                organization_name=validated_data['organization_name'],
                service_type=validated_data['service_type'],
                email=validated_data['email'],
                contact_number=validated_data['contact_number']
            )
            return user
