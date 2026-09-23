from django.contrib import admin
from .models import AboutUs, Testimonial, ClinicFeature

# About Us Admin
@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']
    fieldsets = (
        ('Main Content', {
            'fields': ('title', 'subtitle', 'description', 'image')
        }),
        ('Mission & Vision', {
            'fields': ('mission_text', 'vision_text')
        }),
        ('Features (Enter as JSON array)', {
            'fields': ('features',)
        }),
        ('Statistics', {
            'fields': ('years_experience', 'happy_patients', 'expert_doctors')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

# Testimonial Admin
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'rating', 'treatment', 'is_featured', 'is_active', 'order']
    list_filter = ['rating', 'is_featured', 'is_active']
    search_fields = ['patient_name', 'testimonial_text']
    list_editable = ['is_featured', 'is_active', 'order']
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_name', 'patient_location', 'patient_image')
        }),
        ('Testimonial Details', {
            'fields': ('rating', 'testimonial_text', 'treatment')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )

# Clinic Feature Admin
@admin.register(ClinicFeature)
class ClinicFeatureAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon_class', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'description']