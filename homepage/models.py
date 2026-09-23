from django.db import models

class AboutUs(models.Model):
    """About Us content that can be edited from admin"""
    
    title = models.CharField(max_length=200, default='About Shree Krishna Dental')
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField()
    mission_text = models.TextField(blank=True, null=True)
    vision_text = models.TextField(blank=True, null=True)
    
    # Image field - for about section image
    image = models.ImageField(upload_to='about/', blank=True, null=True, help_text="Upload about section image")
    
    # Features list (as JSON)
    features = models.JSONField(default=list, blank=True)
    
    # Statistics
    years_experience = models.IntegerField(default=10)
    happy_patients = models.IntegerField(default=5000)
    expert_doctors = models.IntegerField(default=15)
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return "About Us Content"
    
    class Meta:
        verbose_name = "About Us"
        verbose_name_plural = "About Us"

class Testimonial(models.Model):
    """Patient testimonials that can be edited from admin"""
    
    patient_name = models.CharField(max_length=200)
    patient_location = models.CharField(max_length=200, blank=True, null=True)
    patient_image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.IntegerField(default=5, choices=[(1,1), (2,2), (3,3), (4,4), (5,5)])
    testimonial_text = models.TextField()
    treatment = models.CharField(max_length=200, blank=True, null=True, help_text="e.g., Dental Implants, LASIK")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
    
    def __str__(self):
        return f"{self.patient_name} - {self.rating}★"

class ClinicFeature(models.Model):
    """Features that can be edited from admin"""
    
    icon_class = models.CharField(max_length=100, default='fas fa-star')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Clinic Feature"
        verbose_name_plural = "Clinic Features"
    
    def __str__(self):
        return self.title

class ClinicFeature(models.Model):
    """Features that can be edited from admin"""
    
    icon_class = models.CharField(max_length=100, default='fas fa-star')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Clinic Feature"
        verbose_name_plural = "Clinic Features"
    
    def __str__(self):
        return self.title