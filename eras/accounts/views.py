from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from datetime import date, datetime
from .forms import (
    CitizenRegistrationForm, ServiceProviderRegistrationForm, 
    CitizenProfileForm, ServiceProviderProfileForm, QuickUpdateForm,
    ServiceProviderRatingForm
)
from .models import CitizenProfile, ServiceProviderProfile, ServiceProviderRating


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
        form = CitizenProfileForm(request.POST or None, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('homepage')
        else:
            print(form.errors)  # For debugging
    else:
        form = CitizenProfileForm(instance=profile)

    return render(request, 'accounts/citizen_profile_setup.html', {
        'form': form,
        'user': request.user,
        'today': date.today()
    })


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


def logout_view(request):
    logout(request)
    return redirect('homepage')




def register_service_provider(request):
    """Service Provider Registration View"""
    if request.method == 'POST':
        form = ServiceProviderRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration successful! Please complete your organization profile.')
                return redirect('service_provider_profile_setup')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ServiceProviderRegistrationForm()
    
    return render(request, 'accounts/register_service_provider.html', {'form': form})


@login_required
def service_provider_profile_setup(request):
    """Service Provider Profile Setup/Update View"""
    if request.user.user_type != 'service_provider':
        messages.error(request, 'Access denied. This page is for service providers only.')
        return redirect('homepage')

    try:
        profile = request.user.service_provider_profile
    except ServiceProviderProfile.DoesNotExist:
        messages.error(request, 'Service provider profile not found.')
        return redirect('homepage')

    if request.method == 'POST':
        form = ServiceProviderProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Mark profile as completed if all required fields are filled
            if profile.is_profile_complete():
                if not profile.profile_completed_at:
                    profile.profile_completed_at = datetime.now()
                    messages.success(request, 'Congratulations! Your profile is now complete.')
            
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            
            # Check if this was a save draft or save & update
            if 'save_draft' in request.POST:
                messages.info(request, 'Profile saved as draft.')
            
            return redirect('service_provider_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ServiceProviderProfileForm(instance=profile)

    context = {
        'form': form,
        'user': request.user,
        'profile': profile,
        'today': date.today(),
        'is_complete': profile.is_profile_complete()
    }
    
    return render(request, 'accounts/service_provider_profile_setup.html', context)


@login_required
def service_provider_dashboard(request):
    """Service Provider Dashboard View"""
    if request.user.user_type != 'service_provider':
        messages.error(request, 'Access denied.')
        return redirect('homepage')

    try:
        profile = request.user.service_provider_profile
    except ServiceProviderProfile.DoesNotExist:
        messages.error(request, 'Profile not found. Please complete your registration.')
        return redirect('service_provider_profile_setup')

    # Get recent emergency responses (you'll implement this when you create the emergency system)
    recent_responses = profile.emergency_responses.all().order_by('-created_at')[:5]
    
    # Calculate average rating
    avg_rating = profile.ratings.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    total_ratings = profile.ratings.count()
    
    # Get capacity percentage
    capacity_percentage = profile.get_capacity_percentage()

    context = {
        'profile': profile,
        'recent_responses': recent_responses,
        'avg_rating': round(avg_rating, 1),
        'total_ratings': total_ratings,
        'capacity_percentage': capacity_percentage,
        'is_complete': profile.is_profile_complete()
    }
    
    return render(request, 'accounts/service_provider_dashboard.html', context)


@login_required
def quick_update_service_provider(request):
    """Quick Update for Service Provider (AJAX)"""
    if request.user.user_type != 'service_provider':
        return JsonResponse({'error': 'Access denied'}, status=403)

    try:
        profile = request.user.service_provider_profile
    except ServiceProviderProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)

    if request.method == 'POST':
        form = QuickUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Information updated successfully',
                'current_capacity': profile.current_capacity,
                'capacity_percentage': profile.get_capacity_percentage(),
                'status': profile.get_current_status_display()
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def service_provider_directory(request):
    """Public Service Provider Directory"""
    providers = ServiceProviderProfile.objects.filter(
        is_verified=True, 
        current_status='active'
    ).select_related('user').prefetch_related('ratings')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    service_type_filter = request.GET.get('service_type', '')
    city_filter = request.GET.get('city', '')
    
    if search_query:
        providers = providers.filter(
            Q(organization_name__icontains=search_query) |
            Q(specialized_services__icontains=search_query)
        )
    
    if service_type_filter:
        providers = providers.filter(service_type=service_type_filter)
    
    if city_filter:
        providers = providers.filter(city__icontains=city_filter)
    
    # Add average rating to each provider
    for provider in providers:
        provider.avg_rating = provider.ratings.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0
        provider.total_ratings = provider.ratings.count()
    
    # Pagination
    paginator = Paginator(providers, 12)  # 12 providers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    service_types = ServiceProviderProfile.SERVICE_TYPE_CHOICES
    cities = ServiceProviderProfile.objects.filter(
        is_verified=True
    ).values_list('city', flat=True).distinct().exclude(city='')
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'service_type_filter': service_type_filter,
        'city_filter': city_filter,
        'service_types': service_types,
        'cities': sorted(cities),
        'total_providers': providers.count()
    }
    
    return render(request, 'accounts/service_provider_directory.html', context)


def service_provider_detail(request, provider_id):
    """Service Provider Detail View"""
    provider = get_object_or_404(
        ServiceProviderProfile.objects.select_related('user').prefetch_related('ratings__user'),
        id=provider_id,
        is_verified=True
    )
    
    # Calculate ratings
    ratings = provider.ratings.all().order_by('-created_at')
    avg_rating = ratings.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    rating_counts = {}
    for i in range(1, 6):
        rating_counts[i] = ratings.filter(rating=i).count()
    
    # Check if current user has already rated
    user_rating = None
    if request.user.is_authenticated:
        user_rating = ratings.filter(user=request.user).first()
    
    # Handle rating submission
    if request.method == 'POST' and request.user.is_authenticated:
        if user_rating:
            messages.warning(request, 'You have already rated this service provider.')
        else:
            rating_form = ServiceProviderRatingForm(request.POST)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.service_provider = provider
                rating.user = request.user
                rating.save()
                messages.success(request, 'Thank you for your rating!')
                return redirect('service_provider_detail', provider_id=provider.id)
    
    rating_form = ServiceProviderRatingForm() if request.user.is_authenticated else None
    
    context = {
        'provider': provider,
        'avg_rating': round(avg_rating, 1),
        'total_ratings': ratings.count(),
        'rating_counts': rating_counts,
        'ratings': ratings[:10],  # Show latest 10 ratings
        'user_rating': user_rating,
        'rating_form': rating_form,
        'capacity_percentage': provider.get_capacity_percentage()
    }
    
    return render(request, 'accounts/service_provider_detail.html', context)


@login_required
def service_provider_settings(request):
    """Service Provider Settings View"""
    if request.user.user_type != 'service_provider':
        messages.error(request, 'Access denied.')
        return redirect('homepage')

    try:
        profile = request.user.service_provider_profile
    except ServiceProviderProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('homepage')

    context = {
        'profile': profile,
        'user': request.user
    }
    
    return render(request, 'accounts/service_provider_settings.html', context)

