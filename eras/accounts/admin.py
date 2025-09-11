from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, CitizenProfile, ServiceProviderProfile, ServiceProviderRating, EmergencyResponse

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone_number', 'is_staff', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number')
        }),
    )


@admin.register(ServiceProviderProfile)
class ServiceProviderProfileAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'service_type', 'city', 'current_status', 'is_verified', 'created_at')
    list_filter = ('service_type', 'current_status', 'is_verified', 'city', 'created_at')
    search_fields = ('organization_name', 'email', 'contact_number', 'registration_number')
    readonly_fields = ('created_at', 'updated_at', 'profile_completed_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'organization_name', 'service_type', 'service_type_other', 'email', 'contact_number')
        }),
        ('Registration Details', {
            'fields': ('registration_number',)
        }),
        ('Location Information', {
            'fields': ('street_address', 'area_sector', 'city', 'postal_code')
        }),
        ('Service Capabilities', {
            'fields': ('specialized_services', 'equipment_available', 'staff_count', 
                      'maximum_capacity', 'average_response_time')
        }),
        ('Contact Information', {
            'fields': ('primary_contact_person', 'contact_person_designation', 
                      'emergency_hotline', 'emergency_email')
        }),
        ('Status & Operations', {
            'fields': ('current_status', 'current_capacity', 'operating_hours')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_at', 'verified_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'profile_completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_providers', 'unverify_providers', 'activate_providers', 'deactivate_providers']
    
    def verify_providers(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} providers verified successfully.')
    verify_providers.short_description = "Verify selected providers"
    
    def unverify_providers(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} providers unverified.')
    unverify_providers.short_description = "Unverify selected providers"
    
    def activate_providers(self, request, queryset):
        updated = queryset.update(current_status='active')
        self.message_user(request, f'{updated} providers activated.')
    activate_providers.short_description = "Activate selected providers"
    
    def deactivate_providers(self, request, queryset):
        updated = queryset.update(current_status='inactive')
        self.message_user(request, f'{updated} providers deactivated.')
    deactivate_providers.short_description = "Deactivate selected providers"


@admin.register(ServiceProviderRating)
class ServiceProviderRatingAdmin(admin.ModelAdmin):
    list_display = ('service_provider', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'service_provider__service_type')
    search_fields = ('service_provider__organization_name', 'user__username')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('service_provider', 'user')


@admin.register(EmergencyResponse)
class EmergencyResponseAdmin(admin.ModelAdmin):
    list_display = ('incident_id', 'service_provider', 'status', 'response_time', 'created_at')
    list_filter = ('status', 'created_at', 'service_provider__service_type')
    search_fields = ('incident_id', 'service_provider__organization_name')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('service_provider')


# admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(CitizenProfile)

# Register your models here.
