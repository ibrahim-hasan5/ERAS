from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CitizenRegistrationForm, ServiceProviderRegistrationForm, CitizenProfileForm
from .models import CitizenProfile


def register_choice(request):
    return render(request, 'accounts/register_choice.html')


def register_citizen(request):
    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'citizen'
            user.save()

            CitizenProfile.objects.create(user=user)
            login(request, user)
            return redirect('homepage')
    else:
        form = CitizenRegistrationForm()
    return render(request, 'accounts/register_citizen.html', {'form': form})


@login_required
def citizen_profile_setup(request):
    if request.user.user_type != 'citizen':
        return redirect('homepage')

    try:
        profile = request.user.citizen_profile
    except CitizenProfile.DoesNotExist:
        profile = CitizenProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = CitizenProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('homepage')
    else:
        form = CitizenProfileForm(instance=profile)

    return render(request, 'accounts/citizen_profile_setup.html', {'form': form})


def register_service_provider(request):
    if request.method == 'POST':
        form = ServiceProviderRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'service_provider'
            user.save()
            login(request, user)
            return redirect('homepage')
    else:
        form = ServiceProviderRegistrationForm()
    return render(request, 'accounts/register_service_provider.html', {'form': form})
