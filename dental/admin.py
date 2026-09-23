from django.contrib import admin
from .models import DentalService, DentalProcedure, DentalFAQ

class DentalProcedureInline(admin.TabularInline):
    model = DentalProcedure
    extra = 1
    fields = ['name', 'description', 'duration', 'price', 'order']

class DentalFAQInline(admin.TabularInline):
    model = DentalFAQ
    extra = 1
    fields = ['question', 'answer', 'order', 'is_active']

@admin.register(DentalService)
class DentalServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'featured', 'is_active', 'order', 'starting_price']
    list_filter = ['service_type', 'featured', 'is_active']
    search_fields = ['name', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['featured', 'is_active', 'order', 'starting_price']
    inlines = [DentalProcedureInline, DentalFAQInline]
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
        ('Pricing', {
            'fields': ('starting_price', 'price_note')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('Status', {
            'fields': ('is_active', 'featured', 'order')
        }),
    )

@admin.register(DentalProcedure)
class DentalProcedureAdmin(admin.ModelAdmin):
    list_display = ['name', 'service', 'duration', 'price', 'order']
    list_filter = ['service']
    search_fields = ['name', 'description']
    list_editable = ['duration', 'price', 'order']

@admin.register(DentalFAQ)
class DentalFAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'service', 'is_active', 'order']
    list_filter = ['service', 'is_active']
    search_fields = ['question', 'answer']
    list_editable = ['is_active', 'order']