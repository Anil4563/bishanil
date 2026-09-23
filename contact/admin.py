from django.contrib import admin
from .models import ContactInquiry, ClinicInfo, SupportTicket, ContactSettings

# Unregister if already registered
try:
    admin.site.unregister(ContactSettings)
except:
    pass

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'inquiry_type', 'subject', 'status', 'created_at']
    list_filter = ['inquiry_type', 'status', 'created_at']
    search_fields = ['name', 'email', 'phone', 'subject', 'message']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ClinicInfo)
class ClinicInfoAdmin(admin.ModelAdmin):
    list_display = ['address_line1', 'phone_primary', 'email_primary']

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'patient_name', 'patient_email', 'subject', 'priority', 'status', 'created_at']
    list_filter = ['priority', 'status', 'created_at']
    search_fields = ['ticket_id', 'patient_name', 'patient_email', 'subject', 'message']
    list_editable = ['priority', 'status']

@admin.register(ContactSettings)
class ContactSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_primary', 'email_primary', 'show_contact_bar']
    fieldsets = (
        ('Phone Numbers (Leave empty to hide)', {
            'fields': ('phone_primary', 'phone_secondary')
        }),
        ('Email Addresses (Leave empty to hide)', {
            'fields': ('email_primary', 'email_support')
        }),
        ('Social Media Links (Leave empty to hide)', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'linkedin_url', 'youtube_url')
        }),
        ('Address (Leave empty to hide)', {
            'fields': ('address', 'working_hours')
        }),
        ('Contact Info Bar (Shows on Homepage)', {
            'fields': ('show_contact_bar', 'bar_address', 'bar_phone', 'bar_email', 'bar_hours')
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        return False