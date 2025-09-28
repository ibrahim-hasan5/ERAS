from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Disaster, DisasterImage, DisasterAlert, DisasterUpdate,
    DisasterResponse, DisasterReport
)


class DisasterImageInline(admin.TabularInline):
    model = DisasterImage
    extra = 1
    readonly_fields = ('uploaded_at', 'image_preview')
    fields = ('image', 'image_preview', 'caption', 'is_primary', 'uploaded_at')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover;" />',
                obj.image.url
            )
        return "No Image"

    image_preview.short_description = "Preview"


class DisasterResponseInline(admin.TabularInline):
    model = DisasterResponse
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('service_provider', 'response_status', 'response_notes', 'created_at')


class DisasterUpdateInline(admin.TabularInline):
    model = DisasterUpdate
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('updated_by', 'update_type', 'notes', 'created_at')


@admin.register(Disaster)
class DisasterAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'disaster_type', 'category', 'severity', 'status',
        'reporter', 'city', 'area_sector', 'created_at', 'auto_approved'
    )
    list_filter = (
        'status', 'disaster_type', 'category', 'severity', 'city',
        'created_at', 'approved_at'
    )
    search_fields = (
        'title', 'description', 'city', 'area_sector', 'reporter__username',
        'reporter__first_name', 'reporter__last_name'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'approved_at', 'resolved_at',
        'view_count', 'disaster_preview'
    )
    raw_id_fields = ('reporter', 'approved_by')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'disaster_type', 'category', 'severity', 'description')
        }),
        ('Location', {
            'fields': ('city', 'area_sector', 'specific_address', 'landmarks')
        }),
        ('Temporal Information', {
            'fields': ('incident_datetime', 'created_at', 'updated_at')
        }),
        ('User Information', {
            'fields': ('reporter', 'emergency_contact')
        }),
        ('Status and Approval', {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Resolution', {
            'fields': ('resolved_at', 'resolution_notes')
        }),
        ('Metadata', {
            'fields': ('view_count', 'is_active', 'disaster_preview')
        }),
    )

    inlines = [DisasterImageInline, DisasterResponseInline, DisasterUpdateInline]

    actions = ['approve_disasters', 'reject_disasters', 'mark_resolved']

    def disaster_preview(self, obj):
        if obj.pk:
            url = reverse('disasters:disaster_detail', args=[obj.pk])
            return format_html(
                '<a href="{}" target="_blank">View Public Page</a>',
                url
            )
        return "Save to view"

    disaster_preview.short_description = "Public View"

    def auto_approved(self, obj):
        return obj.approved_by == obj.reporter
    auto_approved.boolean = True
    auto_approved.short_description = 'Auto-approved'


    def reject_disasters(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{updated} disasters rejected.')

    reject_disasters.short_description = "Reject selected disasters"

    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.exclude(status='resolved').update(
            status='resolved',
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} disasters marked as resolved.')

    mark_resolved.short_description = "Mark as resolved"


@admin.register(DisasterImage)
class DisasterImageAdmin(admin.ModelAdmin):
    list_display = ('disaster', 'image_preview', 'caption', 'is_primary', 'uploaded_at')
    list_filter = ('is_primary', 'uploaded_at')
    search_fields = ('disaster__title', 'caption')
    readonly_fields = ('uploaded_at', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 150px; height: 150px; object-fit: cover;" />',
                obj.image.url
            )
        return "No Image"

    image_preview.short_description = "Preview"


@admin.register(DisasterAlert)
class DisasterAlertAdmin(admin.ModelAdmin):
    list_display = ('disaster', 'user', 'match_type', 'is_read', 'sent_at', 'read_at')
    list_filter = ('is_read', 'match_type', 'sent_at')
    search_fields = ('disaster__title', 'user__username', 'user__email')
    readonly_fields = ('sent_at', 'read_at')
    raw_id_fields = ('disaster', 'user')

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        self.message_user(request, f'{updated} alerts marked as read.')

    mark_as_read.short_description = "Mark selected alerts as read"

    def mark_as_unread(self, request, queryset):
        updated = queryset.filter(is_read=True).update(
            is_read=False,
            read_at=None
        )
        self.message_user(request, f'{updated} alerts marked as unread.')

    mark_as_unread.short_description = "Mark selected alerts as unread"


@admin.register(DisasterUpdate)
class DisasterUpdateAdmin(admin.ModelAdmin):
    list_display = ('disaster', 'updated_by', 'update_type', 'created_at')
    list_filter = ('update_type', 'created_at')
    search_fields = ('disaster__title', 'updated_by__username', 'notes')
    readonly_fields = ('created_at', 'old_values_display', 'new_values_display')
    raw_id_fields = ('disaster', 'updated_by')

    fieldsets = (
        (None, {
            'fields': ('disaster', 'updated_by', 'update_type', 'notes')
        }),
        ('Changes', {
            'fields': ('old_values_display', 'new_values_display'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

    def old_values_display(self, obj):
        if obj.old_values:
            return format_html('<pre>{}</pre>', str(obj.old_values))
        return "No old values"

    old_values_display.short_description = "Old Values"

    def new_values_display(self, obj):
        if obj.new_values:
            return format_html('<pre>{}</pre>', str(obj.new_values))
        return "No new values"

    new_values_display.short_description = "New Values"


@admin.register(DisasterResponse)
class DisasterResponseAdmin(admin.ModelAdmin):
    list_display = (
        'disaster', 'service_provider', 'response_status',
        'estimated_arrival', 'actual_arrival', 'created_at'
    )
    list_filter = ('response_status', 'created_at', 'updated_at')
    search_fields = (
        'disaster__title', 'service_provider__organization_name', 'response_notes'
    )
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('disaster', 'service_provider')

    fieldsets = (
        ('Response Information', {
            'fields': ('disaster', 'service_provider', 'response_status', 'response_notes')
        }),
        ('Timing', {
            'fields': ('estimated_arrival', 'actual_arrival', 'completion_time')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(DisasterReport)
class DisasterReportAdmin(admin.ModelAdmin):
    list_display = (
        'disaster', 'reported_by', 'reason', 'is_reviewed',
        'reviewed_by', 'created_at'
    )
    list_filter = ('reason', 'is_reviewed', 'created_at')
    search_fields = ('disaster__title', 'reported_by__username', 'description')
    readonly_fields = ('created_at',)
    raw_id_fields = ('disaster', 'reported_by', 'reviewed_by')

    fieldsets = (
        ('Report Information', {
            'fields': ('disaster', 'reported_by', 'reason', 'description')
        }),
        ('Review', {
            'fields': ('is_reviewed', 'reviewed_by', 'admin_notes')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

    actions = ['mark_reviewed', 'mark_unreviewed']

    def mark_reviewed(self, request, queryset):
        updated = queryset.filter(is_reviewed=False).update(
            is_reviewed=True,
            reviewed_by=request.user
        )
        self.message_user(request, f'{updated} reports marked as reviewed.')

    mark_reviewed.short_description = "Mark selected reports as reviewed"

    def mark_unreviewed(self, request, queryset):
        updated = queryset.filter(is_reviewed=True).update(
            is_reviewed=False,
            reviewed_by=None
        )
        self.message_user(request, f'{updated} reports marked as unreviewed.')

    mark_unreviewed.short_description = "Mark selected reports as unreviewed"


# Customize admin site headers
admin.site.site_header = "ERAS Disaster Management Admin"
admin.site.site_title = "ERAS Admin Portal"
admin.site.index_title = "Welcome to ERAS Disaster Management System"