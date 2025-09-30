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

    # NEW: Emergency donor flag for quick filtering
    emergency_donor = models.BooleanField(
        default=False, help_text="Available for emergency blood donation")

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


# NEW: Blood Request Model for Sprint 1
class BloodRequest(models.Model):
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    URGENCY_CHOICES = [
        ('urgent', 'Urgent'),
        ('normal', 'Normal'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('fulfilled', 'Fulfilled'),
    ]

    # Public fields (always required)
    requester_name = models.CharField(
        max_length=100, help_text="Person making the request")
    patient_name = models.CharField(
        max_length=100, help_text="Patient who needs blood")
    blood_type_needed = models.CharField(
        max_length=3, choices=BLOOD_TYPE_CHOICES)

    # NEW FIELD - Add after blood_type_needed
    bags_needed = models.PositiveIntegerField(
        default=1,
        help_text="Number of blood bags needed"
    )

    location = models.CharField(
        max_length=200, help_text="Hospital/location where blood is needed")
    contact_phone = models.CharField(max_length=15)
    urgency = models.CharField(
        max_length=10, choices=URGENCY_CHOICES, default='normal')
    needed_by_date = models.DateField(help_text="When is the blood needed by")
    additional_notes = models.TextField(
        blank=True, help_text="Any additional information")

    # Optional tracking (only if logged in)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,
                                   help_text="User who created this request (if logged in)")
    requester_city = models.CharField(max_length=100, blank=True,
                                      help_text="City for filtering purposes")

    # Status and timestamps
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['blood_type_needed']),
            models.Index(fields=['requester_city']),
            models.Index(fields=['status']),
            models.Index(fields=['urgency']),
        ]

    def __str__(self):
        return f"{self.bags_needed} bag(s) of {self.blood_type_needed} needed for {self.patient_name} - {self.get_urgency_display()}"

    def is_urgent(self):
        return self.urgency == 'urgent'


class ServiceProviderProfile(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('hospital', 'Hospital'),
        ('ambulance', 'Ambulance Service'),
        ('fire_station', 'Fire Station'),
        ('police_station', 'Police Station'),
        ('military_camp', 'Military Camp'),
        ('forces_hq', 'Forces Headquarters'),
        ('emergency_response', 'Emergency Response Unit'),
        ('others', 'Others'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='service_provider_profile')

    # Basic Organization Details
    organization_name = models.CharField(max_length=200)
    service_type = models.CharField(
        max_length=20, choices=SERVICE_TYPE_CHOICES)
    service_type_other = models.CharField(max_length=100, blank=True,
                                          help_text="Specify if 'Others' is selected")
    email = models.EmailField()
    contact_number = models.CharField(max_length=15)

    # Extended Profile Fields
    registration_number = models.CharField(max_length=100, blank=True,
                                           help_text="Official registration/license number")

    # Location Information
    street_address = models.CharField(max_length=300, blank=True)
    area_sector = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)

    # Service Capabilities
    specialized_services = models.TextField(blank=True,
                                            help_text="List specialized services offered")
    equipment_available = models.TextField(blank=True,
                                           help_text="List major equipment/resources")
    staff_count = models.PositiveIntegerField(null=True, blank=True)
    maximum_capacity = models.PositiveIntegerField(null=True, blank=True)
    average_response_time = models.PositiveIntegerField(null=True, blank=True,
                                                        help_text="Average response time in minutes")

    # Contact Information
    primary_contact_person = models.CharField(max_length=100, blank=True)
    contact_person_designation = models.CharField(max_length=100, blank=True)
    emergency_hotline = models.CharField(max_length=15, blank=True)
    emergency_email = models.EmailField(blank=True)

    # Status and Operational Info
    current_status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='active')
    current_capacity = models.PositiveIntegerField(null=True, blank=True,
                                                   help_text="Current available capacity")
    operating_hours = models.CharField(
        max_length=200, blank=True, default="24/7")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_completed_at = models.DateTimeField(null=True, blank=True)

    # Verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='verified_providers')

    def __str__(self):
        return f"{self.organization_name} - {self.get_service_type_display()}"

    def is_profile_complete(self):
        required_fields = [
            self.organization_name, self.service_type, self.email,
            self.contact_number, self.street_address, self.area_sector,
            self.city, self.postal_code, self.primary_contact_person,
            self.emergency_hotline
        ]
        return all(field for field in required_fields)

    def get_capacity_percentage(self):
        if self.maximum_capacity and self.current_capacity is not None:
            return round((self.current_capacity / self.maximum_capacity) * 100, 1)
        return None

    def get_service_display_name(self):
        if self.service_type == 'others' and self.service_type_other:
            return self.service_type_other
        return self.get_service_type_display()


class ServiceProviderRating(models.Model):
    service_provider = models.ForeignKey(ServiceProviderProfile, on_delete=models.CASCADE,
                                         related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('service_provider', 'user')

    def __str__(self):
        return f"{self.rating} stars for {self.service_provider.organization_name}"


class EmergencyResponse(models.Model):
    RESPONSE_STATUS_CHOICES = [
        ('received', 'Received'),
        ('dispatched', 'Dispatched'),
        ('on_scene', 'On Scene'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    service_provider = models.ForeignKey(ServiceProviderProfile, on_delete=models.CASCADE,
                                         related_name='emergency_responses')
    incident_id = models.CharField(max_length=50, unique=True)
    response_time = models.PositiveIntegerField(
        help_text="Response time in minutes")
    status = models.CharField(max_length=15, choices=RESPONSE_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.incident_id} - {self.service_provider.organization_name}"
