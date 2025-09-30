from django.shortcuts import render
from accounts.models import BloodRequest, CitizenProfile


def homepage(request):
    """
    Homepage view with blood network data for Sprint 5
    """
    # Get recent blood requests (2 most recent urgent requests)
    recent_blood_requests = BloodRequest.objects.filter(
        status='open'
    ).order_by('-urgency', '-created_at')[:2]

    # Get active donors (4 most recent active donors with blood group)
    active_donors = CitizenProfile.objects.filter(
        available_to_donate='yes'
    ).exclude(
        blood_group__in=['', None]  # Exclude donors without blood group
        # Latest 2 donors
    ).select_related('user').order_by('-last_blood_donation', '-id')[:2]

    context = {
        'recent_blood_requests': recent_blood_requests,
        'active_donors': active_donors,
    }

    return render(request, 'homepage.html', context)


def about_us(request):
    return render(request, 'about_us.html')
