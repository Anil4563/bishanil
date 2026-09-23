from django.db import models

class ContactInquiry(models.Model):
    """
    Model for contact form submissions
    """
    INQUIRY_TYPES = [
        ('general', 'General Inquiry'),
        ('appointment', 'Appointment Related'),
        ('feedback', 'Feedback'),
        ('complaint', 'Complaint'),
        ('career', 'Career Opportunity'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('closed', 'Closed'),
    ]
    
    # Personal Information
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Inquiry Details
    inquiry_type = models.CharField(max_length=50, choices=INQUIRY_TYPES, default='general')
    subject = models.CharField(max_length=300)
    message = models.TextField()
    
    # Additional Info
    preferred_contact = models.CharField(max_length=50, choices=[
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('whatsapp', 'WhatsApp'),
    ], default='email')
    best_time_to_call = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Inquiry'
        verbose_name_plural = 'Contact Inquiries'
    
    def __str__(self):
        return f"{self.name} - {self.subject[:50]}"


class ClinicInfo(models.Model):
    """
    Model for clinic contact information (singleton)
    """
    # Address
    address_line1 = models.CharField(max_length=300, default='Kathmandu, Nepal')
    address_line2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, default='Kathmandu')
    state = models.CharField(max_length=100, default='Bagmati Province')
    country = models.CharField(max_length=100, default='Nepal')
    pincode = models.CharField(max_length=20, default='44600')
    
    # Contact Numbers
    phone_primary = models.CharField(max_length=20, default='+977 9800000000')
    phone_secondary = models.CharField(max_length=20, blank=True)
    emergency_phone = models.CharField(max_length=20, default='+977 9800000000')
    whatsapp_number = models.CharField(max_length=20, default='+977 9800000000')
    
    # Email
    email_primary = models.EmailField(default='info@bishanildental.com')
    email_support = models.EmailField(default='support@bishanildental.com')
    email_appointments = models.EmailField(default='appointments@bishanildental.com')
    
    # Social Media
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    
    # Working Hours
    monday_friday_start = models.TimeField(default='09:00')
    monday_friday_end = models.TimeField(default='20:00')
    saturday_start = models.TimeField(default='10:00')
    saturday_end = models.TimeField(default='17:00')
    sunday_start = models.TimeField(default='10:00')
    sunday_end = models.TimeField(default='17:00')
    is_sunday_open = models.BooleanField(default=True)
    
    # Google Maps
    google_maps_embed_url = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, default=27.7172)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, default=85.3240)
    
    # Clinic Images
    clinic_image = models.ImageField(upload_to='clinic/', blank=True, null=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    
    def __str__(self):
        return "Clinic Information"
    
    class Meta:
        verbose_name = 'Clinic Information'
        verbose_name_plural = 'Clinic Information'
    
    def save(self, *args, **kwargs):
        if not self.pk and ClinicInfo.objects.exists():
            raise ValueError('Only one ClinicInfo instance allowed')
        super().save(*args, **kwargs)


class SupportTicket(models.Model):
    """
    Model for patient support tickets
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    ticket_id = models.CharField(max_length=20, unique=True)
    patient_name = models.CharField(max_length=200)
    patient_email = models.EmailField()
    patient_phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=300)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.CharField(max_length=200, blank=True)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ticket_id} - {self.subject[:50]}"


class ContactSettings(models.Model):
    """Contact information that can be edited from admin"""
    
    # Phone numbers (all optional)
    phone_primary = models.CharField(max_length=20, blank=True, null=True)
    phone_secondary = models.CharField(max_length=20, blank=True, null=True)
    
    # Emails (all optional)
    email_primary = models.EmailField(blank=True, null=True)
    email_support = models.EmailField(blank=True, null=True)
    
    # Social Media Links (all optional)
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    
    # Address (optional)
    address = models.CharField(max_length=300, blank=True, null=True)
    working_hours = models.CharField(max_length=200, blank=True, null=True)
    
    # Contact Info Bar Fields
    show_contact_bar = models.BooleanField(default=True)
    bar_address = models.CharField(max_length=300, blank=True, null=True)
    bar_phone = models.CharField(max_length=20, blank=True, null=True)
    bar_email = models.EmailField(blank=True, null=True)
    bar_hours = models.CharField(max_length=200, blank=True, null=True)
    bar_address_icon = models.CharField(max_length=50, default='fas fa-map-marker-alt')
    bar_phone_icon = models.CharField(max_length=50, default='fas fa-phone-alt')
    bar_email_icon = models.CharField(max_length=50, default='fas fa-envelope')
    bar_hours_icon = models.CharField(max_length=50, default='fas fa-clock')
    
    def save(self, *args, **kwargs):
        if not self.pk and ContactSettings.objects.exists():
            return  # Only allow one instance
        super().save(*args, **kwargs)
    
    def __str__(self):
        return "Contact Settings"
    
    class Meta:
        verbose_name = "Contact Settings"
        verbose_name_plural = "Contact Settings"
        
