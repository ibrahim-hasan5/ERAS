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
    phone_number = forms.CharField(max_length=15, required=True)
    emergency_contact_name = forms.CharField(max_length=100, required=True)
    emergency_contact_phone = forms.CharField(max_length=15, required=True)
    emergency_contact_relationship = forms.CharField(max_length=50, required=True)
    house_road_no = forms.CharField(max_length=200, required=True)
    area_sector = forms.CharField(max_length=100, required=True)
    city = forms.CharField(max_length=100, required=True)
    postal_code = forms.CharField(max_length=10, required=True)
    landmarks = forms.CharField(required=False)
    last_blood_donation = forms.DateField(required=False)
    available_to_donate = forms.ChoiceField(
        choices=[('', 'Select Option'), ('yes', 'Yes'), ('no', 'No')], 
        required=False
    )
    class Meta:
        model = CitizenProfile
        fields = [
            'date_of_birth',
            'blood_group',
            'phone_number',
            'house_road_no',
            'area_sector',
            'city',
            'postal_code',
            'landmarks',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            'last_blood_donation',
            'available_to_donate',
            'medical_conditions',
            'allergies',
            
            
            'regular_medications'
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
