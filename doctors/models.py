from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Doctor(models.Model):
    """
    Model for Doctors (Dental and Eye Specialists)
    """
    SPECIALIZATION_CHOICES = [
        ('dental', 'Dental Specialist'),
        ('eye', 'Eye Specialist'),
    ]
    
    DEGREE_CHOICES = [
        ('bds', 'BDS'),
        ('mds', 'MDS'),
        ('mbbs', 'MBBS'),
        ('md', 'MD'),
        ('ms', 'MS'),
        ('dm', 'DM'),
    ]

    # User link
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='doctor_profile')
    
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    specialization_type = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES)
    specialization = models.CharField(max_length=200, help_text="e.g., Orthodontist, Cataract Surgeon")
    
    # Professional Details
    experience_years = models.IntegerField()
    qualifications = models.TextField(help_text="Detailed qualifications and certifications")
    expertise = models.TextField(help_text="Areas of expertise")
    languages = models.CharField(max_length=200, help_text="e.g., English, Nepali, Hindi")
    
    # Consultation
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    availability = models.CharField(max_length=200, help_text="e.g., Mon-Sat, 10 AM - 6 PM")
    
    # Biography
    bio = models.TextField()
    education = models.JSONField(default=list, help_text="List of education details")
    awards = models.JSONField(default=list, blank=True, help_text="List of awards and achievements")
    memberships = models.JSONField(default=list, blank=True, help_text="Professional memberships")
    
    # Media
    profile_image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    icon_class = models.CharField(max_length=100, default='fas fa-user-md')
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    # Admin Approval Fields for Doctor Registration
    is_approved = models.BooleanField(default=False, help_text="Has admin approved this doctor?")
    registration_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    approved_date = models.DateTimeField(blank=True, null=True)
    approved_by = models.CharField(max_length=200, blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason if rejected")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'
    
    def __str__(self):
        return f"Dr. {self.name} - {self.get_specialization_type_display()}"
    
    def get_absolute_url(self):
        return reverse('doctors:doctor_detail', args=[self.slug])


class DoctorSchedule(models.Model):
    """
    Weekly schedule for each doctor
    """
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedule')
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    notes = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['doctor', 'day', 'start_time']
        unique_together = ['doctor', 'day']
    
    def __str__(self):
        return f"{self.doctor.name} - {self.get_day_display()}: {self.start_time} to {self.end_time}"


class DoctorReview(models.Model):
    """
    Patient reviews for doctors
    """
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    patient_name = models.CharField(max_length=200)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient_name} - {self.doctor.name} - {self.rating}★"

class Prescription(models.Model):
    """
    Medical prescription given by doctor to patient
    """
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='prescriptions')
    patient_name = models.CharField(max_length=200)
    patient_email = models.EmailField()
    patient_phone = models.CharField(max_length=20, blank=True)
    
    # Prescription Details
    diagnosis = models.TextField(help_text="Diagnosis / Medical condition")
    medicines = models.TextField(help_text="List of medicines with dosage")
    instructions = models.TextField(blank=True, help_text="Additional instructions for patient")
    
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
    
    def __str__(self):
        return f"Prescription for {self.patient_name} by Dr. {self.doctor.name} on {self.created_at.date()}"