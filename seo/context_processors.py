from .models import SEOSettings
from django.contrib.sites.models import Site

def seo_settings(request):
    """Add SEO settings to all templates"""
    try:
        settings = SEOSettings.objects.first()
        current_site = Site.objects.get_current()
    except:
        settings = None
        current_site = None
    
    # Determine current page type for meta tags
    path = request.path
    page_type = 'home'
    
    if '/dental/' in path:
        page_type = 'dental'
    elif '/eyecare/' in path:
        page_type = 'eye'
    elif '/doctors/' in path:
        page_type = 'doctors'
    elif '/blog/' in path:
        page_type = 'blog'
    elif '/gallery/' in path:
        page_type = 'gallery'
    elif '/contact/' in path:
        page_type = 'contact'
    elif '/appointments/' in path:
        page_type = 'appointments'
    
    return {
        'seo_settings': settings,
        'current_site': current_site,
        'current_page_type': page_type,
        'current_path': path,
    }