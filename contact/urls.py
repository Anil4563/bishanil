from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.contact_page, name='contact_page'),
    path('submit/', views.submit_inquiry, name='submit_inquiry'),
    path('support/', views.support_ticket, name='support_ticket'),
    path('support/submit/', views.submit_support, name='submit_support'),
]