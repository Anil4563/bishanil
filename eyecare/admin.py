from django.contrib import admin
from .models import EyeService, EyeProcedure, EyeFAQ, EyeTestPackage

class EyeProcedureInline(admin.TabularInline):
    model = EyeProcedure
    extra = 1
    fields = ['name', 'description', 'duration', 'recovery_time', 'price', 'order']

class EyeFAQInline(admin.TabularInline):
    model = EyeFAQ
    extra = 1
    fields = ['question', 'answer', 'order', 'is_active']

@admin.register(EyeService)
class EyeServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'featured', 'is_active', 'order', 'starting_price']
    list_filter = ['service_type', 'featured', 'is_active']
    search_fields = ['name', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['featured', 'is_active', 'order', 'starting_price']
    inlines = [EyeProcedureInline, EyeFAQInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'service_type', 'short_description', 'full_description')
        }),
        ('Media & Icons', {
            'fields': ('icon_class', 'image')
        }),
        ('Benefits & FAQ', {
            'fields': ('benefits', 'faq_title', 'faq_answer')
        }),
        ('Pricing & Duration', {
            'fields': ('starting_price', 'price_note', 'procedure_duration', 'recovery_time')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('Status', {
            'fields': ('is_active', 'featured', 'order')
        }),
    )

@admin.register(EyeProcedure)
class EyeProcedureAdmin(admin.ModelAdmin):
    list_display = ['name', 'service', 'duration', 'recovery_time', 'price', 'order']
    list_filter = ['service']
    search_fields = ['name', 'description']
    list_editable = ['duration', 'recovery_time', 'price', 'order']  # Fixed: recovery_time is now in list_display

@admin.register(EyeFAQ)
class EyeFAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'service', 'is_active', 'order']
    list_filter = ['service', 'is_active']
    search_fields = ['question', 'answer']
    list_editable = ['is_active', 'order']

@admin.register(EyeTestPackage)
class EyeTestPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['price', 'duration', 'is_active', 'order']