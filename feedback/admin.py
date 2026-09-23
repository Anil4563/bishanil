from django.contrib import admin
from .models import ClinicFeedback, DoctorFeedback
from django.utils.safestring import mark_safe
from django.utils import timezone

@admin.register(ClinicFeedback)
class ClinicFeedbackAdmin(admin.ModelAdmin):
    list_display = ['rating_stars', 'name', 'topic', 'show_on_homepage', 'is_approved', 'created_at']
    list_filter = ['rating', 'show_on_homepage', 'is_approved', 'created_at']
    search_fields = ['name', 'email', 'feedback_text', 'topic']
    list_editable = ['show_on_homepage', 'is_approved']
    readonly_fields = ['created_at']
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return mark_safe(f'<span style="color: #ffc107; font-size: 14px;">{stars}</span>')
    rating_stars.short_description = 'Rating'
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Feedback Details', {
            'fields': ('rating', 'feedback_text', 'topic')
        }),
        ('Display Settings', {
            'fields': ('show_on_homepage', 'is_approved')
        }),
        ('Admin Response', {
            'fields': ('admin_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if 'admin_response' in form.changed_data and obj.admin_response:
            obj.responded_by = request.user.username
            obj.responded_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(DoctorFeedback)
class DoctorFeedbackAdmin(admin.ModelAdmin):
    list_display = ['rating_stars', 'name', 'doctor', 'treatment_received', 'show_on_homepage', 'is_approved', 'created_at']
    list_filter = ['rating', 'doctor', 'show_on_homepage', 'is_approved', 'created_at']
    search_fields = ['name', 'email', 'feedback_text', 'treatment_received']
    list_editable = ['show_on_homepage', 'is_approved']
    readonly_fields = ['created_at']
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return mark_safe(f'<span style="color: #ffc107; font-size: 14px;">{stars}</span>')
    rating_stars.short_description = 'Rating'
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Doctor & Treatment', {
            'fields': ('doctor', 'treatment_received', 'appointment_date')
        }),
        ('Feedback Details', {
            'fields': ('rating', 'feedback_text')
        }),
        ('Display Settings', {
            'fields': ('show_on_homepage', 'is_approved')
        }),
        ('Admin Response', {
            'fields': ('admin_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if 'admin_response' in form.changed_data and obj.admin_response:
            obj.responded_by = request.user.username
            obj.responded_at = timezone.now()
        super().save_model(request, obj, form, change)