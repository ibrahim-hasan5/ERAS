from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Disaster, DisasterImage, DisasterResponse, DisasterReport
from accounts.models import CitizenProfile, ServiceProviderProfile
import re


class DisasterForm(forms.ModelForm):
    # Custom fields
    incident_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent'
        }),
        help_text="When did this disaster occur?"
    )

    incident_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent'
        }),
        help_text="What time did this disaster occur?"
    )

    class Meta:
        model = Disaster
        fields = [
            'title', 'disaster_type', 'severity', 'description',
            'city', 'area_sector', 'specific_address', 'landmarks',
            'incident_date', 'incident_time', 'emergency_contact'
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'placeholder': 'Auto-generated if left blank'
            }),
            'disaster_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'onchange': 'updateDisasterCategory(this.value)'
            }),
            'severity': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'rows': 5,
                'placeholder': 'Provide detailed information about the disaster (minimum 50 characters)',
                'onkeyup': 'updateCharCount(this)'
            }),
            'city': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'onchange': 'updateAreaOptions(this.value)'
            }),
            'area_sector': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent'
            }),
            'specific_address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Specific address or location details (optional)'
            }),
            'landmarks': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'placeholder': 'Nearby landmarks for easier identification (optional)'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'placeholder': 'Emergency contact number on scene (optional)'
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Set default incident date/time to now
        if not self.instance.pk:
            now = timezone.now()
            self.fields['incident_date'].initial = now.date()
            self.fields['incident_time'].initial = now.time()

        # Populate city choices from user profiles
        cities = set()
        for profile in CitizenProfile.objects.exclude(city=''):
            if profile.city:
                cities.add(profile.city)
        for profile in ServiceProviderProfile.objects.exclude(city=''):
            if profile.city:
                cities.add(profile.city)

        city_choices = [('', 'Select City')] + [(city, city) for city in sorted(cities)]
        self.fields['city'].widget = forms.Select(choices=city_choices, attrs=self.fields['city'].widget.attrs)

        # Set initial values from user profile if available
        if user and not self.instance.pk:
            try:
                if user.user_type == 'citizen' and hasattr(user, 'citizen_profile'):
                    profile = user.citizen_profile
                    if profile.city:
                        self.fields['city'].initial = profile.city
                    if profile.area_sector:
                        self.fields['area_sector'].initial = profile.area_sector
                elif user.user_type == 'service_provider' and hasattr(user, 'service_provider_profile'):
                    profile = user.service_provider_profile
                    if profile.city:
                        self.fields['city'].initial = profile.city
                    if profile.area_sector:
                        self.fields['area_sector'].initial = profile.area_sector
            except:
                pass

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        # CHANGE: Maximum 50 characters instead of minimum
        if len(description.strip()) > 50:
            raise ValidationError("Description must be 50 characters or less.")
        if len(description.strip()) < 10:  # Optional: Keep minimum 10 characters
            raise ValidationError("Description must be at least 10 characters.")
        return description.strip()

    def clean_emergency_contact(self):
        contact = self.cleaned_data.get('emergency_contact', '')
        if contact and not re.match(r'^\+?[\d\s\-\(\)]+$', contact):
            raise ValidationError("Please enter a valid phone number.")
        return contact

    def clean(self):
        cleaned_data = super().clean()
        incident_date = cleaned_data.get('incident_date')
        incident_time = cleaned_data.get('incident_time')

        if incident_date and incident_time:
            incident_datetime = timezone.datetime.combine(incident_date, incident_time)
            incident_datetime = timezone.make_aware(incident_datetime)

            # Check if incident datetime is not in the future
            if incident_datetime > timezone.now():
                raise ValidationError("Incident date and time cannot be in the future.")

            cleaned_data['incident_datetime'] = incident_datetime

        return cleaned_data

    def save(self, commit=True):
        disaster = super().save(commit=False)

        # Combine date and time
        if 'incident_datetime' in self.cleaned_data:
            disaster.incident_datetime = self.cleaned_data['incident_datetime']

        # Set reporter
        if self.user:
            disaster.reporter = self.user

        if commit:
            disaster.save()

        return disaster


class DisasterImageForm(forms.ModelForm):
    class Meta:
        model = DisasterImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'placeholder': 'Optional image caption'
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'rounded text-red-500 focus:ring-red-500'
            })
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image:
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image size cannot exceed 5MB.")

            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise ValidationError("Only JPEG, PNG, and WebP images are allowed.")

        return image


class DisasterImageFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        # Check maximum number of images (5)
        valid_forms = [form for form in self.forms if form.cleaned_data and not form.cleaned_data.get('DELETE')]
        if len(valid_forms) > 5:
            raise ValidationError("You can upload a maximum of 5 images.")

        # Ensure only one primary image
        primary_count = sum(1 for form in valid_forms if form.cleaned_data.get('is_primary'))
        if primary_count > 1:
            raise ValidationError("Only one image can be marked as primary.")


class DisasterFilterForm(forms.Form):
    disaster_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Disaster.DISASTER_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent'
        })
    )

    severity = forms.ChoiceField(
        choices=[('', 'All Severities')] + Disaster.SEVERITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent'
        })
    )

    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
            'placeholder': 'City'
        })
    )

    area_sector = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
            'placeholder': 'Area/Sector'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent'
        })
    )


class DisasterResponseForm(forms.ModelForm):
    class Meta:
        model = DisasterResponse
        fields = ['response_status', 'response_notes', 'estimated_arrival']
        widgets = {
            'response_status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
            }),
            'response_notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Add response details, current status, or updates...'
            }),
            'estimated_arrival': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
            })
        }

    def clean_estimated_arrival(self):
        estimated_arrival = self.cleaned_data.get('estimated_arrival')
        if estimated_arrival and estimated_arrival < timezone.now():
            raise ValidationError("Estimated arrival time cannot be in the past.")
        return estimated_arrival


class DisasterReportForm(forms.ModelForm):
    class Meta:
        model = DisasterReport
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Please provide details about why you are reporting this disaster...'
            })
        }

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if len(description.strip()) < 10:
            raise ValidationError("Description must be at least 10 characters long.")
        return description.strip()


class AdminDisasterForm(forms.ModelForm):
    """Form for admin to approve/reject disasters"""

    class Meta:
        model = Disaster
        fields = ['status', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'rejection_reason': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Provide reason for rejection (required for rejected status)'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason', '').strip()

        if status == 'rejected' and not rejection_reason:
            raise ValidationError("Rejection reason is required when rejecting a disaster report.")

        return cleaned_data


# Dynamic formset for multiple images
DisasterImageFormSet = forms.formset_factory(
    DisasterImageForm,
    formset=DisasterImageFormSet,
    extra=1,
    max_num=5,
    can_delete=True
)