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
    BLOOD_GROUP_CHOICES = [
        ('', 'Select Blood Group'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='citizen_profile')

    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(
        max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    emergency_contact_relationship = models.CharField(
        max_length=50, blank=True)

    # Address Information
    house_road_no = models.CharField(max_length=200, blank=True)
    area_sector = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    landmarks = models.CharField(max_length=200, blank=True)

    # Blood Donation Info
    last_blood_donation = models.DateField(null=True, blank=True)
    available_to_donate = models.CharField(
        max_length=10,
        choices=[('', 'Select Option'), ('yes', 'Yes'), ('no', 'No')],
        blank=True
    )

    # Additional emergency information
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    regular_medications = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def is_profile_complete(self):
        required_fields = [
            self.date_of_birth, self.blood_group, self.phone_number,
            self.emergency_contact_name, self.emergency_contact_phone,
            self.house_road_no, self.area_sector, self.city, self.postal_code
        ]
        return all(required_fields)
