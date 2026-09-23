from django.contrib import admin
from .models import Doctor, DoctorSchedule, DoctorReview
from django.utils.safestring import mark_safe
from django.utils import timezone

class DoctorScheduleInline(admin.TabularInline):
    model = DoctorSchedule
    extra = 7
    fields = ['day', 'start_time', 'end_time', 'is_available', 'notes']

class DoctorReviewInline(admin.TabularInline):
    model = DoctorReview
    extra = 0
    fields = ['patient_name', 'rating', 'review_text', 'is_approved']
    readonly_fields = ['created_at']

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization_type', 'specialization', 'experience_years', 'consultation_fee', 'is_approved', 'is_featured', 'is_active', 'order']
    list_filter = ['specialization_type', 'specialization', 'is_approved', 'is_featured', 'is_active']
    search_fields = ['name', 'specialization', 'qualifications']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['consultation_fee', 'is_approved', 'is_featured', 'is_active', 'order']
    inlines = [DoctorScheduleInline, DoctorReviewInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    def save_model(self, request, obj, form, change):
        # If status changed to approved, set approval details
        if 'is_approved' in form.changed_data and obj.is_approved:
            obj.approved_date = timezone.now()
            obj.approved_by = request.user.username
            obj.rejection_reason = ''
        super().save_model(request, obj, form, change)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'specialization_type', 'degree', 'specialization')
        }),
        ('Professional Details', {
            'fields': ('experience_years', 'qualifications', 'expertise', 'languages')
        }),
        ('Consultation', {
            'fields': ('consultation_fee', 'availability')
        }),
        ('Biography', {
            'fields': ('bio', 'education', 'awards', 'memberships')
        }),
        ('Media', {
            'fields': ('profile_image', 'icon_class')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('Admin Approval', {
            'fields': ('is_approved', 'rejection_reason', 'approved_date', 'approved_by'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'order')
        }),
    )

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day', 'start_time', 'end_time', 'is_available']
    list_filter = ['doctor', 'day', 'is_available']
    list_editable = ['start_time', 'end_time', 'is_available']

@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'doctor', 'rating', 'is_approved', 'created_at']
    list_filter = ['doctor', 'rating', 'is_approved']
    list_editable = ['is_approved']
    search_fields = ['patient_name', 'review_text']