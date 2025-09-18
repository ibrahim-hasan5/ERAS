from django import template
from django.db.models import Count
from django.utils import timezone
from ..models import Disaster, DisasterAlert

register = template.Library()


@register.simple_tag
def get_recent_disasters(count=3):
    """Get recent approved disasters for homepage display"""
    disasters = Disaster.objects.filter(
        status='approved'
    ).select_related('reporter').prefetch_related('images', 'responses').order_by('-created_at')[:count]

    return disasters


@register.simple_tag
def get_disaster_count():
    """Get total count of approved disasters"""
    return Disaster.objects.filter(status='approved').count()


@register.simple_tag
def get_pending_disasters_count():
    """Get count of pending disasters (for admin)"""
    return Disaster.objects.filter(status='pending').count()


@register.simple_tag(takes_context=True)
def get_user_alerts_count(context):
    """Get unread alerts count for current user"""
    request = context['request']
    if request.user.is_authenticated:
        return DisasterAlert.objects.filter(
            user=request.user,
            is_read=False
        ).count()
    return 0


@register.simple_tag(takes_context=True)
def get_nearby_disasters(context, count=5):
    """Get disasters in user's area"""
    request = context['request']
    if not request.user.is_authenticated:
        return Disaster.objects.none()

    user_city = None
    user_area = None

    try:
        if request.user.user_type == 'citizen' and hasattr(request.user, 'citizen_profile'):
            profile = request.user.citizen_profile
            user_city = profile.city
            user_area = profile.area_sector
        elif request.user.user_type == 'service_provider' and hasattr(request.user, 'service_provider_profile'):
            profile = request.user.service_provider_profile
            user_city = profile.city
            user_area = profile.area_sector
    except:
        pass

    if user_city:
        disasters = Disaster.objects.filter(
            status='approved',
            city=user_city
        ).exclude(reporter=request.user).order_by('-created_at')[:count]

        # Prioritize same area
        if user_area:
            same_area = disasters.filter(area_sector=user_area)
            other_areas = disasters.exclude(area_sector=user_area)
            disasters = list(same_area) + list(other_areas)

        return disasters[:count]

    return Disaster.objects.none()


@register.filter
def disaster_severity_class(severity):
    """Return CSS class for disaster severity"""
    classes = {
        'critical': 'bg-red-100 text-red-800 border-red-200',
        'high': 'bg-orange-100 text-orange-800 border-orange-200',
        'medium': 'bg-yellow-100 text-yellow-800 border-yellow-200',
        'low': 'bg-green-100 text-green-800 border-green-200'
    }
    return classes.get(severity, 'bg-gray-100 text-gray-800 border-gray-200')


@register.filter
def disaster_type_icon(disaster_type):
    """Return Font Awesome icon class for disaster type"""
    icons = {
        'earthquake': 'fas fa-mountain',
        'flood': 'fas fa-water',
        'cyclone_storm': 'fas fa-wind',
        'wildfire': 'fas fa-fire',
        'landslide': 'fas fa-mountain',
        'drought': 'fas fa-sun',
        'tsunami': 'fas fa-water',
        'natural_other': 'fas fa-leaf',
        'building_fire': 'fas fa-fire-extinguisher',
        'industrial_accident': 'fas fa-industry',
        'chemical_spill': 'fas fa-vial',
        'transportation_accident': 'fas fa-car-crash',
        'bomb_threat': 'fas fa-bomb',
        'gas_leak': 'fas fa-gas-pump',
        'structural_collapse': 'fas fa-building',
        'manmade_other': 'fas fa-tools',
    }
    return icons.get(disaster_type, 'fas fa-exclamation-triangle')


@register.simple_tag
def disaster_statistics():
    """Get overall disaster statistics"""
    total = Disaster.objects.filter(status='approved').count()
    today = Disaster.objects.filter(
        status='approved',
        created_at__date=timezone.now().date()
    ).count()
    critical = Disaster.objects.filter(
        status='approved',
        severity='critical'
    ).count()

    return {
        'total': total,
        'today': today,
        'critical': critical
    }


@register.inclusion_tag('disasters/disaster_card.html')
def render_disaster_card(disaster, show_actions=True):
    """Render a disaster card component"""
    return {
        'disaster': disaster,
        'show_actions': show_actions
    }


@register.filter
def time_since(datetime_obj):
    """Return human-readable time since datetime"""
    if not datetime_obj:
        return ""

    now = timezone.now()
    diff = now - datetime_obj

    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"


@register.simple_tag(takes_context=True)
def can_user_respond(context, disaster):
    """Check if current user can respond to disaster"""
    request = context['request']
    if not request.user.is_authenticated:
        return False

    if request.user.user_type != 'service_provider':
        return False

    if disaster.status != 'approved':
        return False

    # Check if user already responded
    if hasattr(request.user, 'service_provider_profile'):
        existing_response = disaster.responses.filter(
            service_provider=request.user.service_provider_profile
        ).exists()
        return not existing_response

    return False


@register.simple_tag
def get_disaster_by_status(status, count=None):
    """Get disasters by status"""
    disasters = Disaster.objects.filter(status=status).order_by('-created_at')
    if count:
        disasters = disasters[:count]
    return disasters


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)


@register.simple_tag
def get_severity_stats():
    """Get disaster count by severity"""
    stats = Disaster.objects.filter(status='approved').values('severity').annotate(
        count=Count('id')
    ).order_by('severity')

    severity_dict = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0
    }

    for stat in stats:
        severity_dict[stat['severity']] = stat['count']

    return severity_dict


@register.simple_tag
def get_disaster_types_stats():
    """Get disaster count by type"""
    stats = Disaster.objects.filter(status='approved').values('disaster_type').annotate(
        count=Count('id')
    ).order_by('-count')

    return stats


@register.filter
def multiply(value, arg):
    """Multiply the value by arg"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value, total):
    """Calculate percentage"""
    try:
        return round((int(value) / int(total)) * 100, 1) if total > 0 else 0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.simple_tag(takes_context=True)
def user_disaster_stats(context):
    """Get disaster statistics for current user"""
    request = context['request']
    if not request.user.is_authenticated:
        return {}

    user_disasters = Disaster.objects.filter(reporter=request.user)

    stats = {
        'total': user_disasters.count(),
        'draft': user_disasters.filter(status='draft').count(),
        'pending': user_disasters.filter(status='pending').count(),
        'approved': user_disasters.filter(status='approved').count(),
        'rejected': user_disasters.filter(status='rejected').count(),
        'resolved': user_disasters.filter(status='resolved').count(),
    }

    return stats


@register.filter
def status_color(status):
    """Return color class for disaster status"""
    colors = {
        'draft': 'text-gray-600 bg-gray-100',
        'pending': 'text-yellow-600 bg-yellow-100',
        'approved': 'text-green-600 bg-green-100',
        'rejected': 'text-red-600 bg-red-100',
        'resolved': 'text-blue-600 bg-blue-100',
        'cancelled': 'text-gray-600 bg-gray-100'
    }
    return colors.get(status, 'text-gray-600 bg-gray-100')