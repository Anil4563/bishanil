from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PatientProfile(models.Model):
    """
    Extended user profile for patients
    """
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Medical Information
    allergies = models.TextField(blank=True, help_text="Any known allergies")
    medical_conditions = models.TextField(blank=True, help_text="Existing medical conditions")
    current_medications = models.TextField(blank=True, help_text="Medications currently taking")
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relation = models.CharField(max_length=100, blank=True)
    
    # Profile
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Patient Profile"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}" or self.user.username
    
    @property
    def get_appointments(self):
        from appointments.models import Appointment
        return Appointment.objects.filter(patient_email=self.user.email)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        PatientProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class MedicalHistory(models.Model):
    """
    Patient's medical history
    """
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_history')
    
    # Medical Conditions
    blood_pressure = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 120/80")
    diabetes = models.BooleanField(default=False)
    thyroid = models.BooleanField(default=False)
    asthma = models.BooleanField(default=False)
    heart_disease = models.BooleanField(default=False)
    allergies = models.TextField(blank=True, null=True, help_text="List any allergies")
    
    # Medications
    current_medications = models.TextField(blank=True, null=True)
    
    # Surgeries
    past_surgeries = models.TextField(blank=True, null=True)
    
    # Family History
    family_history = models.TextField(blank=True, null=True)
    
    # Dental Specific
    last_dental_visit = models.DateField(blank=True, null=True)
    dental_issues = models.TextField(blank=True, null=True)
    
    # Eye Specific
    last_eye_exam = models.DateField(blank=True, null=True)
    glasses_contact_lens = models.CharField(max_length=100, blank=True, null=True)
    eye_issues = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Medical History - {self.patient.user.get_full_name()}"