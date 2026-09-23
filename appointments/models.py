from django.db import models
from django.contrib.auth.models import User
from dental.models import DentalService
from eyecare.models import EyeService
from doctors.models import Doctor

class Appointment(models.Model):
    """
    Model for patient appointments
    """
    SERVICE_TYPE_CHOICES = [
        ('dental', 'Dental Service'),
        ('eye', 'Eye Care Service'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    ATTENDANCE_CHOICES = [
        ('pending', 'Pending'),
        ('came', 'Came to Clinic'),
        ('not_came', 'Did Not Come'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    # Patient Information
    patient_name = models.CharField(max_length=200)
    patient_email = models.EmailField()
    patient_phone = models.CharField(max_length=20)
    patient_age = models.IntegerField(null=True, blank=True)
    
    # Appointment Details
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    dental_service = models.ForeignKey(DentalService, on_delete=models.SET_NULL, null=True, blank=True)
    eye_service = models.ForeignKey(EyeService, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Date & Time
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    
    # Additional Info
    symptoms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Attendance Tracking
    attendance_status = models.CharField(
        max_length=20, 
        choices=ATTENDANCE_CHOICES, 
        default='pending',
        help_text="Did the patient come to the clinic?"
    )
    attendance_notes = models.TextField(blank=True, null=True, help_text="Notes about patient attendance")
    attendance_marked_by = models.CharField(max_length=200, blank=True, null=True)
    attendance_marked_at = models.DateTimeField(blank=True, null=True)
    
    # Rescheduling
    reschedule_requested = models.BooleanField(default=False)
    reschedule_request_date = models.DateField(blank=True, null=True)
    reschedule_request_time = models.TimeField(blank=True, null=True)
    reschedule_reason = models.TextField(blank=True, null=True)
    reschedule_approved = models.BooleanField(default=False)
    reschedule_approved_by = models.CharField(max_length=200, blank=True, null=True)
    
    # Follow-up Appointment Fields
    follow_up_needed = models.BooleanField(default=False, help_text="Does patient need follow-up?")
    follow_up_date = models.DateField(blank=True, null=True, help_text="Suggested follow-up date")
    follow_up_notes = models.TextField(blank=True, null=True, help_text="Doctor's notes for follow-up")
    next_appointment_created = models.BooleanField(default=False, help_text="Has next appointment been created?")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
    
    def __str__(self):
        attendance_icon = ""
        if self.attendance_status == 'came':
            attendance_icon = "✓ "
        elif self.attendance_status == 'not_came':
            attendance_icon = "✗ "
        return f"{attendance_icon}{self.patient_name} - {self.appointment_date} - {self.get_status_display()}"
    
    @property
    def service_name(self):
        if self.service_type == 'dental' and self.dental_service:
            return self.dental_service.name
        elif self.service_type == 'eye' and self.eye_service:
            return self.eye_service.name
        return "Not Specified"
    
    @property
    def is_attended(self):
        return self.attendance_status == 'came'


class AppointmentSlot(models.Model):
    """
    Available time slots for appointments
    """
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_patients = models.IntegerField(default=5)
    booked_count = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['doctor', 'date', 'start_time']
    
    def __str__(self):
        return f"{self.doctor.name} - {self.date} - {self.start_time}"
    
    @property
    def slots_available(self):
        return self.max_patients - self.booked_count


class EmergencyBooking(models.Model):
    """
    Emergency appointment bookings
    """
    patient_name = models.CharField(max_length=200)
    patient_phone = models.CharField(max_length=20)
    patient_age = models.IntegerField()
    emergency_type = models.CharField(max_length=200, help_text="Type of emergency (dental/eye)")
    symptoms = models.TextField()
    preferred_time = models.DateTimeField()
    is_attended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Emergency Booking'
        verbose_name_plural = 'Emergency Bookings'
    
    def __str__(self):
        return f"Emergency: {self.patient_name} - {self.created_at}"

class AppointmentReminder(models.Model):
    """
    Reminders sent to patients for their appointments.
    """
    REMINDER_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('phone', 'Phone Call'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('confirmed', 'Patient Confirmed'),
        ('cancelled', 'Patient Cancelled'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, default='email')
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    
    # AI context (why this reminder was sent)
    risk_level = models.CharField(max_length=20, blank=True, null=True)
    no_show_probability = models.FloatField(blank=True, null=True)
    
    sent_by = models.CharField(max_length=200, blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Appointment Reminder'
        verbose_name_plural = 'Appointment Reminders'
    
    def __str__(self):
        return f"Reminder for {self.appointment.patient_name} - {self.sent_at.strftime('%d %b %Y %H:%M')}"