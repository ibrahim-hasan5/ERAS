from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from PIL import Image
import os

User = get_user_model()


class Disaster(models.Model):
    DISASTER_TYPE_CHOICES = [
        # Natural Disasters
        ('earthquake', 'Earthquake'),
        ('flood', 'Flood'),
        ('cyclone_storm', 'Cyclone/Storm'),
        ('wildfire', 'Fire (Wildfire)'),
        ('landslide', 'Landslide'),
        ('drought', 'Drought'),
        ('tsunami', 'Tsunami'),
        ('natural_other', 'Natural - Others'),

        # Man-Made Disasters
        ('building_fire', 'Building Fire'),
        ('industrial_accident', 'Industrial Accident'),
        ('chemical_spill', 'Chemical Spill'),
        ('transportation_accident', 'Transportation Accident'),
        ('bomb_threat', 'Bomb Threat/Explosion'),
        ('gas_leak', 'Gas Leak'),
        ('structural_collapse', 'Structural Collapse'),
        ('manmade_other', 'Man-Made - Others'),
    ]

    CATEGORY_CHOICES = [
        ('natural', 'Natural Disaster'),
        ('manmade', 'Man-Made Disaster'),
    ]

    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('resolved', 'Resolved'),
        ('cancelled', 'Cancelled'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    disaster_type = models.CharField(max_length=30, choices=DISASTER_TYPE_CHOICES)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    description = models.TextField(help_text="Minimum 50 characters required")

    # Location Information
    city = models.CharField(max_length=100)
    area_sector = models.CharField(max_length=100)
    specific_address = models.TextField(blank=True, help_text="Optional specific address")
    landmarks = models.CharField(max_length=200, blank=True, help_text="Nearby landmarks")

    # Temporal Information
    incident_datetime = models.DateTimeField(help_text="When the disaster actually occurred")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # User Information
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_disasters')
    emergency_contact = models.CharField(max_length=15, blank=True, help_text="Emergency contact on scene")

    # Status and Approval
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_disasters')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # Response Information
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    # Metadata
    view_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'city', 'area_sector']),
            models.Index(fields=['disaster_type', 'severity']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_disaster_type_display()} - {self.city}, {self.area_sector}"

    def save(self, *args, **kwargs):
        # Auto-generate title if not provided
        if not self.title:
            self.title = f"{self.get_disaster_type_display()} in {self.city}"

        # Set category based on disaster type
        natural_types = ['earthquake', 'flood', 'cyclone_storm', 'wildfire',
                         'landslide', 'drought', 'tsunami', 'natural_other']
        if self.disaster_type in natural_types:
            self.category = 'natural'
        else:
            self.category = 'manmade'

        # Set approval timestamp when status changes to approved
        if self.pk:
            old_instance = Disaster.objects.get(pk=self.pk)
            if old_instance.status != 'approved' and self.status == 'approved':
                self.approved_at = timezone.now()

        super().save(*args, **kwargs)

    def get_time_since_reported(self):
        """Return human-readable time since disaster was reported"""
        now = timezone.now()
        diff = now - self.created_at

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"

    def get_severity_color(self):
        """Return CSS class for severity level"""
        colors = {
            'critical': 'text-red-600 bg-red-100',
            'high': 'text-orange-600 bg-orange-100',
            'medium': 'text-yellow-600 bg-yellow-100',
            'low': 'text-green-600 bg-green-100'
        }
        return colors.get(self.severity, 'text-gray-600 bg-gray-100')

    def get_disaster_icon(self):
        """Return Font Awesome icon class for disaster type"""
        icons = {
            'earthquake': 'fas fa-mountain',
            'flood': 'fas fa-water',
            'cyclone_storm': 'fas fa-wind',
            'wildfire': 'fas fa-fire',
            'landslide': 'fas fa-mountain',
            'drought': 'fas fa-sun',
            'tsunami': 'fas fa-water',
            'building_fire': 'fas fa-fire-extinguisher',
            'industrial_accident': 'fas fa-industry',
            'chemical_spill': 'fas fa-vial',
            'transportation_accident': 'fas fa-car-crash',
            'bomb_threat': 'fas fa-bomb',
            'gas_leak': 'fas fa-gas-pump',
            'structural_collapse': 'fas fa-building',
        }
        return icons.get(self.disaster_type, 'fas fa-exclamation-triangle')

    def can_edit(self, user):
        """Check if user can edit this disaster"""
        if user.is_superuser:
            return True
        if self.reporter == user and self.status in ['draft', 'pending', 'rejected']:
            return True
        return False

    def can_delete(self, user):
        """Check if user can delete this disaster"""
        if user.is_superuser:
            return True
        if self.reporter == user and self.status in ['draft', 'rejected']:
            return True
        return False


class DisasterImage(models.Model):
    disaster = models.ForeignKey(Disaster, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='disaster_images/%Y/%m/%d/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_primary', 'uploaded_at']

    def __str__(self):
        return f"Image for {self.disaster.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Resize image if too large
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                img.save(self.image.path, optimize=True, quality=85)

    def delete(self, *args, **kwargs):
        # Delete the actual file when the model instance is deleted
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)


class DisasterAlert(models.Model):
    disaster = models.ForeignKey(Disaster, on_delete=models.CASCADE, related_name='alerts_sent')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_alerts')
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    match_type = models.CharField(max_length=20, choices=[
        ('exact', 'Exact Location Match'),
        ('city', 'Same City'),
        ('critical', 'Critical Override'),
    ])

    class Meta:
        unique_together = ('disaster', 'user')
        ordering = ['-sent_at']

    def __str__(self):
        return f"Alert for {self.user.username} - {self.disaster.title}"


class DisasterUpdate(models.Model):
    disaster = models.ForeignKey(Disaster, on_delete=models.CASCADE, related_name='updates')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    update_type = models.CharField(max_length=20, choices=[
        ('status_change', 'Status Change'),
        ('content_edit', 'Content Edit'),
        ('response_added', 'Response Added'),
        ('resolved', 'Marked as Resolved'),
    ])
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_update_type_display()} - {self.disaster.title}"


class DisasterResponse(models.Model):
    disaster = models.ForeignKey(Disaster, on_delete=models.CASCADE, related_name='responses')
    service_provider = models.ForeignKey('accounts.ServiceProviderProfile',
                                         on_delete=models.CASCADE,
                                         related_name='disaster_responses')
    response_status = models.CharField(max_length=20, choices=[
        ('notified', 'Notified'),
        ('responding', 'Responding'),
        ('on_scene', 'On Scene'),
        ('completed', 'Response Completed'),
        ('cancelled', 'Response Cancelled'),
    ], default='notified')

    response_notes = models.TextField(blank=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    completion_time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('disaster', 'service_provider')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.service_provider.organization_name} - {self.disaster.title}"


class DisasterReport(models.Model):
    """For reporting false or inappropriate disaster reports"""
    disaster = models.ForeignKey(Disaster, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=30, choices=[
        ('false_info', 'False Information'),
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('duplicate', 'Duplicate Report'),
        ('resolved', 'Already Resolved'),
        ('other', 'Other'),
    ])
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='reviewed_reports')
    admin_notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('disaster', 'reported_by')
        ordering = ['-created_at']

    def __str__(self):
        return f"Report: {self.disaster.title} by {self.reported_by.username}"
