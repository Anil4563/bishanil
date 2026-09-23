from django.contrib import admin
from .models import Appointment, AppointmentSlot, EmergencyBooking
from django.utils.safestring import mark_safe
from django.contrib import messages

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['attendance_badge', 'patient_name', 'patient_phone', 'appointment_date', 'doctor', 'status', 'follow_up_needed']
    list_filter = ['status', 'attendance_status', 'follow_up_needed', 'appointment_date', 'doctor']
    search_fields = ['patient_name', 'patient_email', 'patient_phone']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at', 'attendance_marked_at', 'attendance_marked_by', 'next_appointment_created']
    
    def attendance_badge(self, obj):
        if obj.attendance_status == 'came':
            return mark_safe('<span style="background: #4caf50; color: white; padding: 3px 8px; border-radius: 20px; font-size: 11px;">✓ Came</span>')
        elif obj.attendance_status == 'not_came':
            return mark_safe('<span style="background: #f44336; color: white; padding: 3px 8px; border-radius: 20px; font-size: 11px;">✗ Did not come</span>')
        elif obj.attendance_status == 'rescheduled':
            return mark_safe('<span style="background: #ff9800; color: white; padding: 3px 8px; border-radius: 20px; font-size: 11px;">⟳ Rescheduled</span>')
        else:
            return mark_safe('<span style="background: #9e9e9e; color: white; padding: 3px 8px; border-radius: 20px; font-size: 11px;">⏳ Pending</span>')
    attendance_badge.short_description = 'Attendance'
    
    def reschedule_badge(self, obj):
        if obj.reschedule_requested:
            if obj.reschedule_approved:
                return mark_safe('<span style="background: #4caf50; color: white; padding: 3px 8px; border-radius: 20px; font-size: 11px;">✓ Approved</span>')
            else:
                return mark_safe('<span style="background: #ff9800; color: white; padding: 3px 8px; border-radius: 20px; font-size: 11px;">⟳ Requested</span>')
        return mark_safe('<span style="background: #9e9e9e; color: white; padding: 3px 8px; border-radius: 20px; font-size: 11px;">-</span>')
    reschedule_badge.short_description = 'Reschedule'
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_name', 'patient_email', 'patient_phone', 'patient_age')
        }),
        ('Appointment Details', {
            'fields': ('service_type', 'dental_service', 'eye_service', 'doctor', 'appointment_date', 'appointment_time')
        }),
        ('Additional Information', {
            'fields': ('symptoms', 'notes')
        }),
        ('Status & Attendance', {
            'fields': ('status', 'attendance_status', 'attendance_notes', 'attendance_marked_by', 'attendance_marked_at')
        }),
        ('Follow-up Appointment (Schedule Next Visit)', {
            'fields': ('follow_up_needed', 'follow_up_date', 'follow_up_notes', 'next_appointment_created'),
            'description': 'Check "Follow-up Needed" and select a date to automatically schedule the patient\'s next appointment'
        }),
        ('Rescheduling', {
            'fields': ('reschedule_requested', 'reschedule_request_date', 'reschedule_request_time', 'reschedule_reason', 'reschedule_approved', 'reschedule_approved_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Handle attendance marking
        if 'attendance_status' in form.changed_data:
            obj.attendance_marked_by = request.user.username
            from django.utils import timezone
            obj.attendance_marked_at = timezone.now()
        
        # Handle reschedule approval
        if 'reschedule_approved' in form.changed_data and obj.reschedule_approved:
            obj.reschedule_approved_by = request.user.username
            if obj.reschedule_request_date and obj.reschedule_request_time:
                obj.appointment_date = obj.reschedule_request_date
                obj.appointment_time = obj.reschedule_request_time
                obj.reschedule_requested = False
        
        # Save the current appointment first
        super().save_model(request, obj, form, change)
        
        # Check if follow-up is needed and next appointment not created yet
        if obj.follow_up_needed and obj.follow_up_date and not obj.next_appointment_created:
            # Create next appointment
            default_time = obj.appointment_time
            if not default_time:
                from datetime import time
                default_time = time(10, 0)
            
            # Create next appointment
            next_appointment = Appointment.objects.create(
                patient_name=obj.patient_name,
                patient_email=obj.patient_email,
                patient_phone=obj.patient_phone,
                patient_age=obj.patient_age,
                service_type=obj.service_type,
                dental_service=obj.dental_service,
                eye_service=obj.eye_service,
                doctor=obj.doctor,
                appointment_date=obj.follow_up_date,
                appointment_time=default_time,
                symptoms="Follow-up from previous appointment",
                notes=f"Follow-up appointment created by {request.user.username}. Reason: {obj.follow_up_notes}",
                status='pending'
            )
            
            # Mark that next appointment has been created
            obj.next_appointment_created = True
            obj.save(update_fields=['next_appointment_created'])
            
            messages.success(request, f'✅ Follow-up appointment created for {obj.patient_name} on {obj.follow_up_date}')

@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'start_time', 'end_time', 'max_patients', 'booked_count', 'slots_available', 'is_available']
    list_filter = ['doctor', 'date', 'is_available']
    list_editable = ['max_patients', 'is_available']
    search_fields = ['doctor__name']
    
    def slots_available(self, obj):
        return obj.slots_available
    slots_available.short_description = 'Available Slots'

@admin.register(EmergencyBooking)
class EmergencyBookingAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'patient_phone', 'emergency_type', 'preferred_time', 'is_attended', 'created_at']
    list_filter = ['emergency_type', 'is_attended']
    search_fields = ['patient_name', 'patient_phone']
    list_editable = ['is_attended']

from .models import Appointment, AppointmentSlot, EmergencyBooking, AppointmentReminder


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'reminder_type', 'status', 'risk_level', 'sent_by', 'sent_at']
    list_filter = ['reminder_type', 'status', 'risk_level', 'sent_at']
    search_fields = ['appointment__patient_name', 'appointment__patient_email', 'message']
    readonly_fields = ['sent_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Appointment', {
            'fields': ('appointment',)
        }),
        ('Reminder Details', {
            'fields': ('reminder_type', 'message', 'status')
        }),
        ('AI Context', {
            'fields': ('risk_level', 'no_show_probability')
        }),
        ('Metadata', {
            'fields': ('sent_by', 'sent_at', 'notes')
        }),
    )