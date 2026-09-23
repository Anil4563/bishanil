from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.feedback_page, name='feedback_page'),
    path('clinic/', views.submit_clinic_feedback, name='submit_clinic_feedback'),
    path('doctor/<int:doctor_id>/', views.submit_doctor_feedback, name='submit_doctor_feedback'),
]