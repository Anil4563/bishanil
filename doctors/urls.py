from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.doctor_list, name='doctor_list'),
    path('register/', views.doctor_register, name='doctor_register'),
    path('login/', views.doctor_login, name='doctor_login'),
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('give-prescription/', views.give_prescription, name='give_prescription'),
    path('view-prescription/<int:prescription_id>/', views.view_prescription, name='view_prescription'),
    path('print-prescription/<int:prescription_id>/', views.print_prescription, name='print_prescription'),
    path('patient-details/<str:patient_email>/', views.view_patient_details, name='patient_details'),  
    path('similar-patients/<str:patient_email>/', views.similar_patients_doctor, name='similar_patients_doctor'),
    path('<slug:slug>/', views.doctor_detail, name='doctor_detail'),
]