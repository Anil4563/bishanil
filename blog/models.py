from django.db import models
from django.urls import reverse
from django.utils import timezone

class BlogCategory(models.Model):
    """
    Categories for blog posts
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category', args=[self.slug])


class BlogTag(models.Model):
    """
    Tags for blog posts
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:tag', args=[self.slug])


class BlogPost(models.Model):
    """
    Main blog post model
    """
    POST_TYPES = [
        ('dental', 'Dental Care'),
        ('eye', 'Eye Care'),
        ('general', 'General Health'),
        ('news', 'Clinic News'),
        ('tips', 'Health Tips'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='general')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(BlogTag, blank=True, related_name='posts')
    
    # Content
    excerpt = models.TextField(max_length=500, help_text="Short summary shown in blog listings")
    content = models.TextField(help_text="Full blog content (HTML supported)")
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    
    # Author
    author_name = models.CharField(max_length=200, default='Bishanil Team')
    author_image = models.ImageField(upload_to='blog/authors/', blank=True, null=True)
    author_bio = models.TextField(blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    
    # Statistics
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])
    
    @property
    def reading_time(self):
        """Calculate reading time in minutes"""
        word_count = len(self.content.split())
        minutes = max(1, round(word_count / 200))
        return minutes


class BlogComment(models.Model):
    """
    Comments on blog posts
    """
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"
