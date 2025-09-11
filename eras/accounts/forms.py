from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import User, CitizenProfile, ServiceProviderProfile, ServiceProviderRating


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


class ServiceProviderRegistrationForm(UserCreationForm):
    # Organization details
    organization_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter organization name'
        }),
        help_text='This will be used as your username'
    )
    
    service_type = forms.ChoiceField(
        choices=ServiceProviderProfile.SERVICE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Select your service type'
    )
    
    service_type_other = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Please specify',
            'style': 'display: none;'  # Hidden by default
        }),
        help_text='Specify if "Others" is selected'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'organization@example.com'
        }),
        help_text='Official organization email'
    )
    
    contact_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+880 xxx xxx xxxx'
        })
    )

    class Meta:
        model = User
        fields = ('organization_name', 'service_type', 'service_type_other', 
                  'email', 'contact_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field since we'll use organization_name
        if 'username' in self.fields:
            del self.fields['username']
        
        # Style password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Add JavaScript for conditional field display
        self.fields['service_type'].widget.attrs.update({
            'onchange': 'toggleOtherField(this.value)'
        })

    def clean_organization_name(self):
        organization_name = self.cleaned_data['organization_name']
        # Check if organization name already exists as username
        if User.objects.filter(username=organization_name.lower().replace(' ', '_')).exists():
            raise forms.ValidationError(
                "An organization with this name already exists. Please choose a different name."
            )
        return organization_name

    def clean(self):
        cleaned_data = super().clean()
        service_type = cleaned_data.get('service_type')
        service_type_other = cleaned_data.get('service_type_other')
        
        if service_type == 'others' and not service_type_other:
            raise forms.ValidationError({
                'service_type_other': 'Please specify the service type when "Others" is selected.'
            })
        
        return cleaned_data

    def save(self, commit=True):
        # Create username from organization name
        organization_name = self.cleaned_data['organization_name']
        username = organization_name.lower().replace(' ', '_').replace('-', '_')
        
        user = super().save(commit=False)
        user.username = username
        user.email = self.cleaned_data['email']
        user.user_type = 'service_provider'
        user.phone_number = self.cleaned_data['contact_number']
        
        if commit:
            user.save()
            
            # Create ServiceProviderProfile
            ServiceProviderProfile.objects.create(
                user=user,
                organization_name=self.cleaned_data['organization_name'],
                service_type=self.cleaned_data['service_type'],
                service_type_other=self.cleaned_data.get('service_type_other', ''),
                email=self.cleaned_data['email'],
                contact_number=self.cleaned_data['contact_number']
            )
        
        return user


class ServiceProviderProfileForm(forms.ModelForm):
    class Meta:
        model = ServiceProviderProfile
        fields = [
            'organization_name', 'service_type', 'service_type_other',
            'email', 'contact_number', 'registration_number',
            'street_address', 'area_sector', 'city', 'postal_code',
            'specialized_services', 'equipment_available', 'staff_count',
            'maximum_capacity', 'average_response_time',
            'primary_contact_person', 'contact_person_designation',
            'emergency_hotline', 'emergency_email', 'current_capacity',
            'operating_hours'
        ]
        
        widgets = {
            'organization_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Organization Name'
            }),
            'service_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'service_type_other': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Please specify'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'organization@example.com'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+880 xxx xxx xxxx'
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Official registration number'
            }),
            'street_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'area_sector': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Area/Sector'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal Code'
            }),
            'specialized_services': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List specialized services offered'
            }),
            'equipment_available': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List major equipment and resources'
            }),
            'staff_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'maximum_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'average_response_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Minutes'
            }),
            'primary_contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact person name'
            }),
            'contact_person_designation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Designation/Title'
            }),
            'emergency_hotline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact number'
            }),
            'emergency_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'emergency@organization.com'
            }),
            'current_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'operating_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '24/7 or specify hours'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make certain fields required
        required_fields = [
            'organization_name', 'service_type', 'email', 'contact_number',
            'street_address', 'area_sector', 'city', 'postal_code',
            'primary_contact_person', 'emergency_hotline'
        ]
        
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
                self.fields[field_name].widget.attrs['required'] = 'required'

    def clean(self):
        cleaned_data = super().clean()
        service_type = cleaned_data.get('service_type')
        service_type_other = cleaned_data.get('service_type_other')
        current_capacity = cleaned_data.get('current_capacity')
        maximum_capacity = cleaned_data.get('maximum_capacity')
        
        # Validate service_type_other
        if service_type == 'others' and not service_type_other:
            raise forms.ValidationError({
                'service_type_other': 'Please specify the service type when "Others" is selected.'
            })
        
        # Validate capacity
        if current_capacity is not None and maximum_capacity is not None:
            if current_capacity > maximum_capacity:
                raise forms.ValidationError({
                    'current_capacity': 'Current capacity cannot exceed maximum capacity.'
                })
        
        return cleaned_data


class QuickUpdateForm(forms.ModelForm):
    """Form for quick updates of frequently changed information"""
    class Meta:
        model = ServiceProviderProfile
        fields = ['current_capacity', 'contact_number', 'current_status', 'operating_hours']
        
        widgets = {
            'current_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'current_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'operating_hours': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }


class ServiceProviderRatingForm(forms.ModelForm):
    class Meta:
        model = ServiceProviderRating
        fields = ['rating', 'review']
        
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'review': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience (optional)'
            }),
        }