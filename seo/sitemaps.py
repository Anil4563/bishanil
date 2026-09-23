from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import BlogPost
from dental.models import DentalService
from eyecare.models import EyeService
from doctors.models import Doctor

class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return ['homepage', 'dental:service_list', 'eyecare:service_list', 
                'doctors:doctor_list', 'contact:contact_page', 'gallery:gallery_home']
    
    def location(self, item):
        return reverse(item)

class BlogSitemap(Sitemap):
    """Sitemap for blog posts"""
    priority = 0.6
    changefreq = 'weekly'
    
    def items(self):
        return BlogPost.objects.filter(status='published')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()

class DentalServiceSitemap(Sitemap):
    """Sitemap for dental services"""
    priority = 0.7
    changefreq = 'monthly'
    
    def items(self):
        return DentalService.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()

class EyeServiceSitemap(Sitemap):
    """Sitemap for eye care services"""
    priority = 0.7
    changefreq = 'monthly'
    
    def items(self):
        return EyeService.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()

class DoctorSitemap(Sitemap):
    """Sitemap for doctors"""
    priority = 0.6
    changefreq = 'monthly'
    
    def items(self):
        return Doctor.objects.filter(is_active=True)
    
    def location(self, obj):
        return obj.get_absolute_url()