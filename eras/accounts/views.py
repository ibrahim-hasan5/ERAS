from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from .forms import CitizenRegistrationForm, ServiceProviderRegistrationForm

def register_choice(request):
    return render(request, 'accounts/register_choice.html')

def register_citizen(request):
    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'citizen'
            user.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CitizenRegistrationForm()
    return render(request, 'accounts/register_citizen.html', {'form': form})

def register_service_provider(request):
    if request.method == 'POST':
        form = ServiceProviderRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'service_provider'
            user.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = ServiceProviderRegistrationForm()
    return render(request, 'accounts/register_service_provider.html', {'form': form})

def dashboard(request):
    return render(request, 'dashboard.html', {'user': request.user})