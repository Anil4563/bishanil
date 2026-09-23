from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.gallery_home, name='gallery_home'),
    path('category/<slug:slug>/', views.category_view, name='category_view'),
    path('image/<int:id>/', views.image_detail, name='image_detail'),
    path('achievements/', views.achievements_view, name='achievements'),
]