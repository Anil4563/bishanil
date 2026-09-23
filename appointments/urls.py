from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('emergency/', views.emergency_booking, name='emergency_booking'),
    path('success/', views.booking_success, name='booking_success'),
    path('get-slots/', views.get_available_slots, name='get_slots'),
]