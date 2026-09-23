from django.urls import path
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, BlogSitemap, DentalServiceSitemap, EyeServiceSitemap, DoctorSitemap
from . import views



app_name = 'seo'

urlpatterns = [
        path('robots.txt', views.robots_txt, name='robots'),
]