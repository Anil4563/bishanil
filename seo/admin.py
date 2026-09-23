from django.contrib import admin
from .models import SEOSettings, PageSEO

@admin.register(SEOSettings)
class SEOSettingsAdmin(admin.ModelAdmin):
    list_display = ['site', 'site_name', 'is_active', 'updated_at']
    fieldsets = (
        ('Site Information', {
            'fields': ('site', 'site_name', 'site_tagline', 'site_description', 'site_keywords')
        }),
        ('Social Media URLs', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'youtube_url', 'linkedin_url')
        }),
        ('Schema Markup', {
            'fields': ('business_type', 'business_logo')
        }),
        ('Open Graph (Social Sharing)', {
            'fields': ('og_title', 'og_description', 'og_image')
        }),
        ('Twitter Card', {
            'fields': ('twitter_card_type', 'twitter_site')
        }),
        ('Verification Codes', {
            'fields': ('google_verification', 'bing_verification', 'yandex_verification')
        }),
        ('Analytics', {
            'fields': ('google_analytics_id', 'google_tag_manager_id')
        }),
        ('Custom Code', {
            'fields': ('custom_header_code', 'custom_footer_code')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(PageSEO)
class PageSEOAdmin(admin.ModelAdmin):
    list_display = ['page_type', 'meta_title', 'no_index', 'no_follow', 'is_active']
    list_filter = ['page_type', 'no_index', 'no_follow', 'is_active']
    search_fields = ['meta_title', 'meta_description']
    fieldsets = (
        ('Page Information', {
            'fields': ('page_type', 'page_url')
        }),
        ('Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url')
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image')
        }),
        ('Schema Markup', {
            'fields': ('schema_type', 'custom_schema')
        }),
        ('Indexing', {
            'fields': ('no_index', 'no_follow')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )