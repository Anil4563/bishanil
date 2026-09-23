from django.db import models
from django.contrib.sites.models import Site
from django.utils.html import strip_tags

class SEOSettings(models.Model):
    """
    Global SEO settings for the website
    """
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='seo_settings')
    
    # Site Information
    site_name = models.CharField(max_length=200, default='Bishanil Dental & Eye Care')
    site_tagline = models.CharField(max_length=300, blank=True)
    site_description = models.TextField(max_length=500, default='Best dental and eye care services in Kathmandu, Nepal. Expert doctors, advanced technology, affordable prices.')
    site_keywords = models.CharField(max_length=500, default='dental clinic, eye care, dentist, ophthalmologist, tooth implant, cataract surgery, LASIK')
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Schema Markup
    business_type = models.CharField(max_length=100, default='MedicalClinic')
    business_logo = models.ImageField(upload_to='seo/', blank=True, null=True)
    
    # Open Graph (Social Sharing)
    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.TextField(max_length=500, blank=True)
    og_image = models.ImageField(upload_to='seo/og/', blank=True, null=True)
    
    # Twitter Card
    twitter_card_type = models.CharField(max_length=50, choices=[
        ('summary', 'Summary'),
        ('summary_large_image', 'Summary with Large Image'),
    ], default='summary_large_image')
    twitter_site = models.CharField(max_length=100, blank=True)
    
    # Verification Codes
    google_verification = models.CharField(max_length=200, blank=True, help_text="Google Search Console verification code")
    bing_verification = models.CharField(max_length=200, blank=True)
    yandex_verification = models.CharField(max_length=200, blank=True)
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True)
    google_tag_manager_id = models.CharField(max_length=50, blank=True)
    
    # Additional
    custom_header_code = models.TextField(blank=True, help_text="Custom code to add to <head> section")
    custom_footer_code = models.TextField(blank=True, help_text="Custom code to add before </body>")
    
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'SEO Setting'
        verbose_name_plural = 'SEO Settings'
    
    def __str__(self):
        return f"SEO Settings for {self.site.name}"
    
    def save(self, *args, **kwargs):
        if not self.pk and SEOSettings.objects.exists():
            raise ValueError('Only one SEOSettings instance allowed')
        super().save(*args, **kwargs)


class PageSEO(models.Model):
    """
    SEO settings for individual pages
    """
    PAGE_TYPES = [
        ('home', 'Homepage'),
        ('about', 'About Us'),
        ('dental_services', 'Dental Services'),
        ('eye_services', 'Eye Care Services'),
        ('doctors', 'Doctors'),
        ('contact', 'Contact'),
        ('blog', 'Blog'),
        ('gallery', 'Gallery'),
    ]
    
    page_type = models.CharField(max_length=50, choices=PAGE_TYPES, unique=True)
    page_url = models.CharField(max_length=300, blank=True, help_text="Custom URL if not standard")
    
    # Meta Tags
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=500, blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    canonical_url = models.URLField(blank=True)
    
    # Open Graph
    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.TextField(max_length=500, blank=True)
    og_image = models.ImageField(upload_to='seo/page_og/', blank=True, null=True)
    
    # Schema
    schema_type = models.CharField(max_length=100, blank=True)
    custom_schema = models.JSONField(default=dict, blank=True)
    
    # Indexing
    no_index = models.BooleanField(default=False, help_text="Add noindex meta tag")
    no_follow = models.BooleanField(default=False, help_text="Add nofollow meta tag")
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Page SEO'
        verbose_name_plural = 'Page SEO'
    
    def __str__(self):
        return f"SEO for {self.get_page_type_display()}"
