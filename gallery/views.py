from django.shortcuts import render, get_object_or_404
from .models import GalleryCategory, GalleryImage, VideoGallery, Achievement

def gallery_home(request):
    """Main gallery page showing all categories"""
    categories = GalleryCategory.objects.filter(is_active=True)
    
    # Get featured images from each category
    featured_images = {}
    for category in categories:
        images = category.images.filter(is_featured=True, is_active=True)[:4]
        if images:
            featured_images[category.id] = images
    
    # Get featured videos
    featured_videos = VideoGallery.objects.filter(is_featured=True, is_active=True)[:3]
    
    # Get recent images
    recent_images = GalleryImage.objects.filter(is_active=True)[:12]
    
    context = {
        'categories': categories,
        'featured_images': featured_images,
        'featured_videos': featured_videos,
        'recent_images': recent_images,
    }
    return render(request, 'gallery/gallery_home.html', context)

def category_view(request, slug):
    """View images and videos for a specific category"""
    category = get_object_or_404(GalleryCategory, slug=slug, is_active=True)
    images = category.images.filter(is_active=True)
    videos = category.videos.filter(is_active=True)
    
    # Separate before/after images
    before_after_images = images.filter(is_before_after=True)
    regular_images = images.filter(is_before_after=False)
    
    context = {
        'category': category,
        'regular_images': regular_images,
        'before_after_images': before_after_images,
        'videos': videos,
    }
    return render(request, 'gallery/category_view.html', context)

def image_detail(request, id):
    """View single image detail"""
    image = get_object_or_404(GalleryImage, id=id, is_active=True)
    
    # Get next and previous images in same category
    category_images = list(image.category.images.filter(is_active=True).values_list('id', flat=True))
    current_index = category_images.index(image.id) if image.id in category_images else -1
    
    prev_id = category_images[current_index - 1] if current_index > 0 else None
    next_id = category_images[current_index + 1] if current_index < len(category_images) - 1 else None
    
    context = {
        'image': image,
        'prev_id': prev_id,
        'next_id': next_id,
    }
    return render(request, 'gallery/image_detail.html', context)

def achievements_view(request):
    """View all achievements and awards"""
    achievements = Achievement.objects.filter(is_active=True)
    context = {
        'achievements': achievements,
    }
    return render(request, 'gallery/achievements.html', context)