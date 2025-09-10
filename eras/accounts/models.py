from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPES = (
        ('citizen', 'Citizen'),
        ('service_provider', 'Service Provider'),
    )

    user_type = models.CharField(
        max_length=20, choices=USER_TYPES, default='citizen')
    phone_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.username


class CitizenProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='citizen_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
