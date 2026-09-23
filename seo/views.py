from django.http import HttpResponse
from .models import SEOSettings

def robots_txt(request):
    """Generate dynamic robots.txt file"""
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/login/",
        "Disallow: /accounts/logout/",
        "Disallow: /accounts/register/",
        "Disallow: /appointments/emergency/",
        "",
        "Sitemap: https://www.shreekrishnadental.com/sitemap.xml",
        "",
        "# Crawl delay",
        "Crawl-delay: 1",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")