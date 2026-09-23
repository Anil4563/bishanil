from django.db import models
from doctors.models import Doctor

class ClinicFeedback(models.Model):
    """
    Feedback for the clinic
    """
    RATING_CHOICES = [
        (1, '⭐ 1 Star - Poor'),
        (2, '⭐⭐ 2 Stars - Fair'),
        (3, '⭐⭐⭐ 3 Stars - Good'),
        (4, '⭐⭐⭐⭐ 4 Stars - Very Good'),
        (5, '⭐⭐⭐⭐⭐ 5 Stars - Excellent'),
    ]
    
    # Person giving feedback
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Feedback details
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    feedback_text = models.TextField()
    
    # What about
    topic = models.CharField(max_length=200, blank=True, null=True, help_text="e.g., Cleanliness, Staff Behavior, Treatment Quality")
    
    # Display on website
    show_on_homepage = models.BooleanField(default=False, help_text="Show this feedback on homepage")
    is_approved = models.BooleanField(default=False, help_text="Approve to show on website")
    
    # Admin response
    admin_response = models.TextField(blank=True, null=True, help_text="Admin can respond to feedback")
    responded_by = models.CharField(max_length=200, blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Clinic Feedback'
        verbose_name_plural = 'Clinic Feedbacks'
    
    def __str__(self):
        return f"{self.name} - {self.rating}★ - {self.created_at.date()}"


class DoctorFeedback(models.Model):
    """
    Feedback for individual doctors
    """
    RATING_CHOICES = [
        (1, '⭐ 1 Star - Poor'),
        (2, '⭐⭐ 2 Stars - Fair'),
        (3, '⭐⭐⭐ 3 Stars - Good'),
        (4, '⭐⭐⭐⭐ 4 Stars - Very Good'),
        (5, '⭐⭐⭐⭐⭐ 5 Stars - Excellent'),
    ]
    
    # Person giving feedback
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Doctor
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='feedbacks')
    
    # Feedback details
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    feedback_text = models.TextField()
    
    # Treatment info
    treatment_received = models.CharField(max_length=200, blank=True, null=True)
    appointment_date = models.DateField(blank=True, null=True)
    
    # Display on website
    show_on_homepage = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False, help_text="Approve to show on website")
    
    # Admin response
    admin_response = models.TextField(blank=True, null=True)
    responded_by = models.CharField(max_length=200, blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Doctor Feedback'
        verbose_name_plural = 'Doctor Feedbacks'
    
    def __str__(self):
        return f"{self.name} - Dr. {self.doctor.name} - {self.rating}★"