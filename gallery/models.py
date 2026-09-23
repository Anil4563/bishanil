from django.db import models

class GalleryCategory(models.Model):
    """
    Categories for gallery items
    """
    CATEGORY_TYPES = [
        ('clinic', 'Clinic & Facility'),
        ('before_after', 'Before & After'),
        ('events', 'Events & Camp'),
        ('team', 'Team & Doctors'),
        ('patients', 'Happy Patients'),
        ('equipment', 'Equipment & Technology'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category_type = models.CharField(max_length=50, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    icon_class = models.CharField(max_length=50, default='fas fa-images')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Gallery Category'
        verbose_name_plural = 'Gallery Categories'
    
    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    """
    Images for gallery
    """
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='images')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='gallery/images/')
    
    # For before/after images
    before_image = models.ImageField(upload_to='gallery/before_after/', blank=True, null=True)
    after_image = models.ImageField(upload_to='gallery/before_after/', blank=True, null=True)
    is_before_after = models.BooleanField(default=False)
    
    # For dental/eye specific
    service_type = models.CharField(max_length=20, choices=[
        ('dental', 'Dental'),
        ('eye', 'Eye Care'),
        ('both', 'Both'),
    ], default='both')
    
    # Meta
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Date
    date_added = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-date_added']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'
    
    def __str__(self):
        return self.title
    
    @property
    def get_image_url(self):
        if self.is_before_after and self.after_image:
            return self.after_image.url
        return self.image.url if self.image else ''


class VideoGallery(models.Model):
    """
    Videos for gallery (YouTube/Vimeo embed)
    """
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='videos', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_url = models.URLField(help_text="YouTube or Vimeo URL")
    thumbnail = models.ImageField(upload_to='gallery/video_thumbnails/', blank=True, null=True)
    service_type = models.CharField(max_length=20, choices=[
        ('dental', 'Dental'),
        ('eye', 'Eye Care'),
        ('both', 'Both'),
    ], default='both')
    order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_added = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-date_added']
        verbose_name = 'Video Gallery'
        verbose_name_plural = 'Video Galleries'
    
    def __str__(self):
        return self.title
    
    def get_embed_url(self):
        """Convert YouTube URL to embed URL"""
        if 'youtube.com' in self.video_url or 'youtu.be' in self.video_url:
            if 'youtu.be' in self.video_url:
                video_id = self.video_url.split('/')[-1]
            else:
                video_id = self.video_url.split('v=')[-1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif 'vimeo.com' in self.video_url:
            video_id = self.video_url.split('/')[-1]
            return f"https://player.vimeo.com/video/{video_id}"
        return self.video_url


class Achievement(models.Model):
    """
    Clinic achievements, awards, milestones
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon_class = models.CharField(max_length=50, default='fas fa-trophy')
    year = models.IntegerField()
    image = models.ImageField(upload_to='gallery/achievements/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-year', 'order']
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'
    
    def __str__(self):
        return f"{self.title} - {self.year}"