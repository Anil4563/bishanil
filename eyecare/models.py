from django.db import models
from django.urls import reverse

class EyeService(models.Model):
    """
    Model for Eye Care Services like Cataract, LASIK, Retina Service, etc.
    """
    SERVICE_TYPES = [
        ('checkup', 'Eye Checkup'),
        ('cataract', 'Cataract Surgery'),
        ('lasik', 'LASIK'),
        ('retina', 'Retina Service'),
        ('glaucoma', 'Glaucoma'),
        ('contact_lens', 'Contact Lens'),
        ('optical', 'Optical Store'),
        ('vision_therapy', 'Vision Therapy'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    icon_class = models.CharField(max_length=100, default='fas fa-eye')
    image = models.ImageField(upload_to='services/eyecare/', blank=True, null=True)
    
    # Benefits list (store as JSON)
    benefits = models.JSONField(default=list, blank=True)
    
    # FAQ for this service
    faq_title = models.CharField(max_length=300, blank=True)
    faq_answer = models.TextField(blank=True)
    
    # Meta info for SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    
    # Pricing
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_note = models.CharField(max_length=200, blank=True)
    
    # Surgery duration
    procedure_duration = models.CharField(max_length=100, blank=True)
    recovery_time = models.CharField(max_length=200, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Eye Care Service'
        verbose_name_plural = 'Eye Care Services'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('eyecare:service_detail', args=[self.slug])


class EyeProcedure(models.Model):
    """
    Sub-procedures under each eye care service
    """
    service = models.ForeignKey(EyeService, on_delete=models.CASCADE, related_name='procedures')
    name = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.CharField(max_length=100, blank=True, help_text="e.g., 15-30 minutes")
    recovery_time = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.service.name} - {self.name}"


class EyeFAQ(models.Model):
    """
    Frequently Asked Questions for Eye Care Services
    """
    service = models.ForeignKey(EyeService, on_delete=models.CASCADE, related_name='faqs', null=True, blank=True)
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'question']
    
    def __str__(self):
        return self.question


class EyeTestPackage(models.Model):
    """
    Comprehensive eye test packages
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    includes = models.JSONField(default=list)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name