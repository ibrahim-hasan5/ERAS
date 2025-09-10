from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


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
