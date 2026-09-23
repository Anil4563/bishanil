from django.contrib import admin
from .models import BlogCategory, BlogTag, BlogPost, BlogComment

class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 0
    fields = ['name', 'email', 'comment', 'is_approved']
    readonly_fields = ['created_at']

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']

@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'post_type', 'category', 'status', 'is_featured', 'views', 'published_at']
    list_filter = ['post_type', 'category', 'status', 'is_featured', 'published_at']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['status', 'is_featured']
    readonly_fields = ['views', 'likes', 'created_at', 'updated_at']
    inlines = [BlogCommentInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'post_type', 'category', 'tags')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Author', {
            'fields': ('author_name', 'author_image', 'author_bio')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Statistics', {
            'fields': ('views', 'likes')
        }),
        ('Status', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'comment_preview', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['name', 'email', 'comment']
    list_editable = ['is_approved']
    
    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment'