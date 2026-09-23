from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class SimpleSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return [
            '/',
            '/dental/services/',
            '/eyecare/services/',
            '/doctors/',
            '/gallery/',
            '/blog/',
            '/contact/',
            '/appointments/book/',
        ]
    
    def location(self, item):
        return item