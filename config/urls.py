from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.contrib.sitemaps.views import sitemap
from seo.simple_sitemap import SimpleSitemap
from django.conf import settings
from django.conf.urls.static import static

sitemaps = {'pages': SimpleSitemap}

def robots_txt(request):
    return HttpResponse("User-agent: *\nAllow: /\nSitemap: http://127.0.0.1:8000/sitemap.xml", content_type="text/plain")

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', robots_txt, name='robots'),
    # path('admin/', admin.site.urls),  # REMOVED default admin
    
    path('', include('homepage.urls')),
    path('dental/', include('dental.urls')),
    path('eyecare/', include('eyecare.urls')),
    path('doctors/', include('doctors.urls')),
    path('appointments/', include('appointments.urls')),
    path('contact/', include('contact.urls')),
    path('gallery/', include('gallery.urls')),
    path('blog/', include('blog.urls')),
    path('accounts/', include('accounts.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('seo/', include('seo.urls')),
    path('payments/', include('payments.urls')),
    path('feedback/', include('feedback.urls')),
    path('admin-panel/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
