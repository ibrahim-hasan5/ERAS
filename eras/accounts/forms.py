from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, CitizenProfile


class CitizenRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number',
                  'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CitizenProfileForm(forms.ModelForm):
    class Meta:
        model = CitizenProfile
        fields = [
            'date_of_birth', 'blood_group', 'emergency_contact',
            'present_division', 'present_district', 'present_upazila',
            'present_post_office', 'present_post_code', 'present_address_details',
            'permanent_division', 'permanent_district', 'permanent_upazila',
            'permanent_post_office', 'permanent_post_code', 'permanent_address_details',
            'frequent_division', 'frequent_district', 'frequent_upazila',
            'frequent_post_office', 'frequent_post_code', 'frequent_address_details',
            'medical_conditions', 'allergies', 'regular_medications'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'date_of_birth'
            }),
            'blood_group': forms.Select(attrs={
                'class': 'form-control',
                'id': 'blood_group'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+880 xxx xxx xxxx'
            }),
            'present_address_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'House number, road, area details'
            }),
            'permanent_address_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'House number, road, area details'
            }),
            'frequent_address_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'House number, road, area details'
            }),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'e.g., Diabetes, Heart condition'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'e.g., Penicillin, Peanuts'
            }),
            'regular_medications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'e.g., Insulin, Blood pressure medication'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.widgets:
                field.widget.attrs['class'] = 'form-control'

            # Make certain fields required
            if field_name in ['date_of_birth', 'blood_group', 'emergency_contact',
                              'present_division', 'present_district']:
                field.required = True
                field.widget.attrs['required'] = 'required'
            else:
                field.required = False


class ServiceProviderRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number',
                  'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
