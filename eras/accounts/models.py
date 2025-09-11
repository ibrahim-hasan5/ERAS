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

    DIVISION_CHOICES = [
        ('', 'Select Division'),
        ('dhaka', 'Dhaka'),
        ('chattogram', 'Chattogram'),
        ('khulna', 'Khulna'),
        ('rajshahi', 'Rajshahi'),
        ('barishal', 'Barishal'),
        ('sylhet', 'Sylhet'),
        ('rangpur', 'Rangpur'),
        ('mymensingh', 'Mymensingh'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='citizen_profile')

    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(
        max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)

    # Present Address
    present_division = models.CharField(
        max_length=50, choices=DIVISION_CHOICES, blank=True)
    present_district = models.CharField(max_length=100, blank=True)
    present_upazila = models.CharField(max_length=100, blank=True)
    present_post_office = models.CharField(max_length=100, blank=True)
    present_post_code = models.CharField(max_length=10, blank=True)
    present_address_details = models.TextField(blank=True)

    # Permanent Address
    permanent_division = models.CharField(
        max_length=50, choices=DIVISION_CHOICES, blank=True)
    permanent_district = models.CharField(max_length=100, blank=True)
    permanent_upazila = models.CharField(max_length=100, blank=True)
    permanent_post_office = models.CharField(max_length=100, blank=True)
    permanent_post_code = models.CharField(max_length=10, blank=True)
    permanent_address_details = models.TextField(blank=True)

    # Frequent Address (for those who move frequently)
    frequent_division = models.CharField(
        max_length=50, choices=DIVISION_CHOICES, blank=True)
    frequent_district = models.CharField(max_length=100, blank=True)
    frequent_upazila = models.CharField(max_length=100, blank=True)
    frequent_post_office = models.CharField(max_length=100, blank=True)
    frequent_post_code = models.CharField(max_length=10, blank=True)
    frequent_address_details = models.TextField(blank=True)

    # Additional emergency information
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    regular_medications = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def is_profile_complete(self):
        required_fields = [
            self.date_of_birth, self.blood_group, self.emergency_contact,
            self.present_division, self.present_district
        ]
        return all(required_fields)
