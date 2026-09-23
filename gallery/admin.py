from django.contrib import admin
from .models import GalleryCategory, GalleryImage, VideoGallery, Achievement

class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1
    fields = ['title', 'image', 'is_before_after', 'before_image', 'after_image', 'order', 'is_featured', 'is_active']

class VideoGalleryInline(admin.TabularInline):
    model = VideoGallery
    extra = 1
    fields = ['title', 'video_url', 'thumbnail', 'order', 'is_featured', 'is_active']

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'order', 'is_active']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    inlines = [GalleryImageInline, VideoGalleryInline]

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'service_type', 'is_before_after', 'is_featured', 'order', 'is_active']
    list_filter = ['category', 'service_type', 'is_before_after', 'is_featured', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_featured', 'is_active']

@admin.register(VideoGallery)
class VideoGalleryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'service_type', 'is_featured', 'order', 'is_active']
    list_filter = ['category', 'service_type', 'is_featured', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_featured', 'is_active']

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['title', 'year', 'order', 'is_active']
    list_filter = ['year', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_active']