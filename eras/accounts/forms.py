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
        fields = ['date_of_birth', 'address',
                  'blood_group', 'emergency_contact', 'location']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select Blood Group'),
                ('A+', 'A+'),
                ('A-', 'A-'),
                ('B+', 'B+'),
                ('B-', 'B-'),
                ('AB+', 'AB+'),
                ('AB-', 'AB-'),
                ('O+', 'O+'),
                ('O-', 'O-'),
            ]),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }


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
