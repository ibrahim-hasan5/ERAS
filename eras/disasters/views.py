from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.forms import formset_factory
from django.db import transaction
import json

from .models import (
    Disaster, DisasterImage, DisasterAlert, DisasterUpdate,
    DisasterResponse, DisasterReport
)
from .forms import (
    DisasterForm, DisasterImageForm, DisasterFilterForm,
    DisasterResponseForm, DisasterReportForm, AdminDisasterForm,
    DisasterImageFormSet
)
from accounts.models import User, CitizenProfile, ServiceProviderProfile


# ===== DISASTER CREATION & MANAGEMENT =====

@login_required
def create_disaster(request):
    """Create a new disaster report"""
    if request.method == 'POST':
        form = DisasterForm(request.POST, user=request.user)
        image_formset = DisasterImageFormSet(request.POST, request.FILES)

        if form.is_valid() and image_formset.is_valid():
            try:
                with transaction.atomic():
                    # Save disaster
                    disaster = form.save()

                    # Save images
                    for image_form in image_formset:
                        if image_form.cleaned_data and not image_form.cleaned_data.get('DELETE'):
                            if image_form.cleaned_data.get('image'):
                                image = image_form.save(commit=False)
                                image.disaster = disaster
                                image.save()

                    # Create update record
                    DisasterUpdate.objects.create(
                        disaster=disaster,
                        updated_by=request.user,
                        update_type='content_edit',
                        notes=f"Disaster report created: {disaster.title}"
                    )

                    messages.success(request, 'Disaster report created successfully!')

                    # Redirect based on action
                    if 'save_draft' in request.POST:
                        return redirect('disaster_detail', disaster_id=disaster.id)
                    else:
                        disaster.status = 'pending'
                        disaster.save()
                        messages.info(request, 'Disaster report submitted for review!')
                        return redirect('disasters:my_disasters')

            except Exception as e:
                messages.error(request, f'Error creating disaster report: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DisasterForm(user=request.user)
        image_formset = DisasterImageFormSet()

    context = {
        'form': form,
        'image_formset': image_formset,
        'is_create': True,
    }
    return render(request, 'disasters/create_disaster.html', context)




@login_required
def edit_disaster(request, disaster_id):
    """Edit an existing disaster report"""
    disaster = get_object_or_404(Disaster, id=disaster_id)

    # Check permissions
    if not disaster.can_edit(request.user):
        messages.error(request, 'You do not have permission to edit this disaster report.')
        return redirect('disaster_detail', disaster_id=disaster.id)

    # Define ImageFormSet ONCE here
    ImageFormSet = formset_factory(DisasterImageForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = DisasterForm(request.POST, instance=disaster, user=request.user)
        image_formset = ImageFormSet(request.POST, request.FILES)

        if form.is_valid() and image_formset.is_valid():
            try:
                with transaction.atomic():
                    # Store old values
                    old_values = {
                        'title': disaster.title,
                        'disaster_type': disaster.disaster_type,
                        'severity': disaster.severity,
                        'description': disaster.description,
                    }

                    # Save disaster
                    disaster = form.save()

                    # Handle images
                    for image_form in image_formset:
                        if image_form.cleaned_data:
                            if image_form.cleaned_data.get('DELETE'):
                                image_id = image_form.cleaned_data.get('id')
                                if image_id:
                                    image_id.delete()
                            elif image_form.cleaned_data.get('image'):
                                image = image_form.save(commit=False)
                                image.disaster = disaster
                                image.save()

                    # Track updates
                    new_values = {
                        'title': disaster.title,
                        'disaster_type': disaster.disaster_type,
                        'severity': disaster.severity,
                        'description': disaster.description,
                    }

                    DisasterUpdate.objects.create(
                        disaster=disaster,
                        updated_by=request.user,
                        update_type='content_edit',
                        old_values=old_values,
                        new_values=new_values,
                        notes=f"Disaster report updated"
                    )

                    messages.success(request, 'Disaster report updated successfully!')
                    return redirect('disaster_detail', disaster_id=disaster.id)

            except Exception as e:
                messages.error(request, f'Error updating disaster report: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DisasterForm(instance=disaster, user=request.user)
        image_formset = ImageFormSet(initial=[
            {'image': img.image, 'caption': img.caption, 'is_primary': img.is_primary, 'id': img}
            for img in disaster.images.all()
        ])

    context = {
        'form': form,
        'image_formset': image_formset,
        'disaster': disaster,
        'is_create': False,
    }
    return render(request, 'disasters/create_disaster.html', context)



@login_required
def delete_disaster(request, disaster_id):
    """Delete a disaster report"""
    disaster = get_object_or_404(Disaster, id=disaster_id)

    # Check permissions
    if not disaster.can_delete(request.user):
        messages.error(request, 'You do not have permission to delete this disaster report.')
        return redirect('disaster_detail', disaster_id=disaster.id)

    if request.method == 'POST':
        disaster_title = disaster.title
        disaster.delete()
        messages.success(request, f'Disaster report "{disaster_title}" has been deleted.')
        return redirect('my_disasters')

    context = {'disaster': disaster}
    return render(request, 'disasters/delete_disaster.html', context)


# ===== DISASTER VIEWING =====

def disaster_list(request):
    """Public disaster list page"""
    disasters = Disaster.objects.filter(status='approved').select_related('reporter')

    # Apply filters
    form = DisasterFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('disaster_type'):
            disasters = disasters.filter(disaster_type=form.cleaned_data['disaster_type'])
        if form.cleaned_data.get('severity'):
            disasters = disasters.filter(severity=form.cleaned_data['severity'])
        if form.cleaned_data.get('city'):
            disasters = disasters.filter(city__icontains=form.cleaned_data['city'])
        if form.cleaned_data.get('area_sector'):
            disasters = disasters.filter(area_sector__icontains=form.cleaned_data['area_sector'])
        if form.cleaned_data.get('date_from'):
            disasters = disasters.filter(created_at__date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            disasters = disasters.filter(created_at__date__lte=form.cleaned_data['date_to'])

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        disasters = disasters.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(area_sector__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(disasters, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'filter_form': form,
        'search_query': search_query,
        'total_disasters': disasters.count(),
    }
    return render(request, 'disasters/disaster_list.html', context)


def disaster_detail(request, disaster_id):
    """Detailed disaster view"""
    disaster = get_object_or_404(
        Disaster.objects.select_related('reporter').prefetch_related(
            'images', 'responses__service_provider', 'updates'
        ),
        id=disaster_id
    )

    # Check if user can view this disaster
    if disaster.status not in ['approved', 'resolved']:
        if not request.user.is_authenticated:
            raise Http404("Disaster not found")
        if disaster.reporter != request.user and not request.user.is_superuser:
            raise Http404("Disaster not found")

    # Increment view count
    disaster.view_count += 1
    disaster.save(update_fields=['view_count'])

    # Get responses and updates
    responses = disaster.responses.select_related('service_provider').order_by('-created_at')
    updates = disaster.updates.select_related('updated_by').order_by('-created_at')[:10]

    # Forms for authenticated users
    response_form = None
    report_form = None

    if request.user.is_authenticated:
        # Service provider response form
        if (request.user.user_type == 'service_provider' and
                hasattr(request.user, 'service_provider_profile')):
            response_form = DisasterResponseForm()

        # Report form for inappropriate content
        report_form = DisasterReportForm()

    # Check if current user already responded (for service providers)
    user_response = None
    if (request.user.is_authenticated and
            request.user.user_type == 'service_provider' and
            hasattr(request.user, 'service_provider_profile')):
        user_response = responses.filter(
            service_provider=request.user.service_provider_profile
        ).first()

    context = {
        'disaster': disaster,
        'responses': responses,
        'updates': updates,
        'response_form': response_form,
        'report_form': report_form,
        'user_response': user_response,
        'can_edit': disaster.can_edit(request.user) if request.user.is_authenticated else False,
        'can_delete': disaster.can_delete(request.user) if request.user.is_authenticated else False,
    }
    return render(request, 'disasters/disaster_detail.html', context)


@login_required
def my_disasters(request):
    """User's disaster reports dashboard"""
    disasters = Disaster.objects.filter(reporter=request.user).order_by('-created_at')

    # Statistics
    stats = {
        'total': disasters.count(),
        'draft': disasters.filter(status='draft').count(),
        'pending': disasters.filter(status='pending').count(),
        'approved': disasters.filter(status='approved').count(),
        'rejected': disasters.filter(status='rejected').count(),
        'resolved': disasters.filter(status='resolved').count(),
    }

    # Pagination
    paginator = Paginator(disasters, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'stats': stats,
    }
    return render(request, 'disasters/my_disasters.html', context)


# ===== SERVICE PROVIDER RESPONSES =====

@login_required
def add_response(request, disaster_id):
    """Service provider response to disaster"""
    if request.user.user_type != 'service_provider':
        messages.error(request, 'Only service providers can respond to disasters.')
        return redirect('disaster_detail', disaster_id=disaster_id)

    disaster = get_object_or_404(Disaster, id=disaster_id, status='approved')
    service_provider = request.user.service_provider_profile

    # Check if already responded
    existing_response = DisasterResponse.objects.filter(
        disaster=disaster,
        service_provider=service_provider
    ).first()

    if request.method == 'POST':
        if existing_response:
            form = DisasterResponseForm(request.POST, instance=existing_response)
        else:
            form = DisasterResponseForm(request.POST)

        if form.is_valid():
            response = form.save(commit=False)
            response.disaster = disaster
            response.service_provider = service_provider
            response.save()

            # Create update record
            DisasterUpdate.objects.create(
                disaster=disaster,
                updated_by=request.user,
                update_type='response_added',
                notes=f"Response updated by {service_provider.organization_name}"
            )

            messages.success(request, 'Response updated successfully!')
            return redirect('disaster_detail', disaster_id=disaster.id)
    else:
        if existing_response:
            form = DisasterResponseForm(instance=existing_response)
        else:
            form = DisasterResponseForm()

    context = {
        'disaster': disaster,
        'form': form,
        'existing_response': existing_response,
    }
    return render(request, 'disasters/add_response.html', context)


@login_required
def nearby_disasters(request):
    """Service provider nearby disasters"""
    if request.user.user_type != 'service_provider':
        messages.error(request, 'Access denied.')
        return redirect('homepage')

    try:
        profile = request.user.service_provider_profile
    except:
        messages.error(request, 'Service provider profile not found.')
        return redirect('homepage')

    # Get disasters in same city/area
    disasters = Disaster.objects.filter(
        status='approved',
        city=profile.city
    ).select_related('reporter').prefetch_related('responses')

    # Prioritize disasters in same area
    same_area = disasters.filter(area_sector=profile.area_sector)
    other_areas = disasters.exclude(area_sector=profile.area_sector)

    # Combine with same area first
    disasters = list(same_area) + list(other_areas)

    # Add response status for each disaster
    for disaster in disasters:
        disaster.user_response = disaster.responses.filter(
            service_provider=profile
        ).first()

    context = {
        'disasters': disasters,
        'profile': profile,
    }
    return render(request, 'disasters/nearby_disasters.html', context)


# ===== REPORTING & MODERATION =====

@login_required
def report_disaster(request, disaster_id):
    """Report inappropriate disaster content"""
    disaster = get_object_or_404(Disaster, id=disaster_id)

    # Check if user already reported
    existing_report = DisasterReport.objects.filter(
        disaster=disaster,
        reported_by=request.user
    ).first()

    if existing_report:
        messages.warning(request, 'You have already reported this disaster.')
        return redirect('disaster_detail', disaster_id=disaster.id)

    if request.method == 'POST':
        form = DisasterReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.disaster = disaster
            report.reported_by = request.user
            report.save()

            messages.success(request, 'Report submitted successfully. We will review it shortly.')
            return redirect('disaster_detail', disaster_id=disaster.id)
    else:
        form = DisasterReportForm()

    context = {
        'disaster': disaster,
        'form': form,
    }
    return render(request, 'disasters/report_disaster.html', context)


# ===== ADMIN FUNCTIONS =====

@login_required
def admin_disasters(request):
    """Admin disaster management"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('homepage')

    disasters = Disaster.objects.select_related('reporter').order_by('-created_at')

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        disasters = disasters.filter(status=status_filter)

    # Statistics
    stats = {
        'total': Disaster.objects.count(),
        'pending': Disaster.objects.filter(status='pending').count(),
        'approved': Disaster.objects.filter(status='approved').count(),
        'rejected': Disaster.objects.filter(status='rejected').count(),
        'reports': DisasterReport.objects.filter(is_reviewed=False).count(),
    }

    # Pagination
    paginator = Paginator(disasters, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'stats': stats,
        'status_filter': status_filter,
        'status_choices': Disaster.STATUS_CHOICES,
    }
    return render(request, 'disasters/admin_disasters.html', context)


@login_required
def approve_disaster(request, disaster_id):
    """Admin approve/reject disaster"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('homepage')

    disaster = get_object_or_404(Disaster, id=disaster_id)

    if request.method == 'POST':
        form = AdminDisasterForm(request.POST, instance=disaster)
        if form.is_valid():
            old_status = disaster.status
            disaster = form.save(commit=False)

            if disaster.status == 'approved' and old_status != 'approved':
                disaster.approved_by = request.user
                disaster.approved_at = timezone.now()

                # Send alerts to matching users
                send_disaster_alerts(disaster)

            disaster.save()

            # Create update record
            DisasterUpdate.objects.create(
                disaster=disaster,
                updated_by=request.user,
                update_type='status_change',
                old_values={'status': old_status},
                new_values={'status': disaster.status},
                notes=f"Status changed from {old_status} to {disaster.status}"
            )

            messages.success(request, f'Disaster {disaster.get_status_display().lower()} successfully!')
            return redirect('admin_disasters')
    else:
        form = AdminDisasterForm(instance=disaster)

    context = {
        'disaster': disaster,
        'form': form,
    }
    return render(request, 'disasters/approve_disaster.html', context)


# ===== AJAX & API VIEWS =====

def get_areas_by_city(request):
    """AJAX endpoint to get areas by city"""
    city = request.GET.get('city', '')
    if not city:
        return JsonResponse({'areas': []})

    # Get areas from both citizen and service provider profiles
    citizen_areas = CitizenProfile.objects.filter(
        city=city
    ).exclude(area_sector='').values_list('area_sector', flat=True).distinct()

    service_areas = ServiceProviderProfile.objects.filter(
        city=city
    ).exclude(area_sector='').values_list('area_sector', flat=True).distinct()

    # Combine and sort
    all_areas = set(list(citizen_areas) + list(service_areas))
    areas = [{'value': area, 'label': area} for area in sorted(all_areas)]

    return JsonResponse({'areas': areas})


@login_required
def mark_resolved(request, disaster_id):
    """Mark disaster as resolved"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    disaster = get_object_or_404(Disaster, id=disaster_id)

    # Check permissions
    if disaster.reporter != request.user and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Permission denied'})

    disaster.status = 'resolved'
    disaster.resolved_at = timezone.now()
    disaster.save()

    # Create update record
    DisasterUpdate.objects.create(
        disaster=disaster,
        updated_by=request.user,
        update_type='resolved',
        notes="Disaster marked as resolved"
    )

    return JsonResponse({
        'success': True,
        'message': 'Disaster marked as resolved',
        'new_status': disaster.get_status_display()
    })


# ===== UTILITY FUNCTIONS =====

def send_disaster_alerts(disaster):
    """Send alerts to matching users when disaster is approved"""
    from django.db.models import Q

    # Get all users with profiles in the same location
    citizen_profiles = CitizenProfile.objects.filter(
        city=disaster.city
    ).select_related('user')

    service_profiles = ServiceProviderProfile.objects.filter(
        city=disaster.city
    ).select_related('user')

    alerts_to_create = []

    # Process citizen profiles
    for profile in citizen_profiles:
        match_type = 'city'
        if profile.area_sector == disaster.area_sector:
            match_type = 'exact'
        elif disaster.severity == 'critical':
            match_type = 'critical'

        # Create alert if not already exists
        if not DisasterAlert.objects.filter(disaster=disaster, user=profile.user).exists():
            alerts_to_create.append(DisasterAlert(
                disaster=disaster,
                user=profile.user,
                match_type=match_type
            ))

    # Process service provider profiles
    for profile in service_profiles:
        match_type = 'city'
        if profile.area_sector == disaster.area_sector:
            match_type = 'exact'
        elif disaster.severity == 'critical':
            match_type = 'critical'

        # Create alert if not already exists
        if not DisasterAlert.objects.filter(disaster=disaster, user=profile.user).exists():
            alerts_to_create.append(DisasterAlert(
                disaster=disaster,
                user=profile.user,
                match_type=match_type
            ))

    # Bulk create alerts
    if alerts_to_create:
        DisasterAlert.objects.bulk_create(alerts_to_create, ignore_conflicts=True)

    return len(alerts_to_create)


@login_required
def user_alerts(request):
    """Get user's unread alerts"""
    alerts = DisasterAlert.objects.filter(
        user=request.user,
        is_read=False
    ).select_related('disaster').order_by('-sent_at')

    alert_data = []
    for alert in alerts:
        alert_data.append({
            'id': alert.id,
            'disaster_id': alert.disaster.id,
            'title': alert.disaster.title,
            'disaster_type': alert.disaster.get_disaster_type_display(),
            'severity': alert.disaster.severity,
            'location': f"{alert.disaster.city}, {alert.disaster.area_sector}",
            'description': alert.disaster.description[:100] + '...' if len(
                alert.disaster.description) > 100 else alert.disaster.description,
            'time_reported': alert.disaster.get_time_since_reported(),
            'sent_at': alert.sent_at.strftime('%Y-%m-%d %H:%M'),
            'match_type': alert.get_match_type_display(),
        })

    return JsonResponse({
        'alerts': alert_data,
        'count': len(alert_data)
    })


@login_required
def mark_alert_read(request, alert_id):
    """Mark alert as read"""
    if request.method != 'POST':
        return JsonResponse({'success': False})

    try:
        alert = DisasterAlert.objects.get(id=alert_id, user=request.user)
        alert.is_read = True
        alert.read_at = timezone.now()
        alert.save()
        return JsonResponse({'success': True})
    except DisasterAlert.DoesNotExist:
        return JsonResponse({'success': False})
