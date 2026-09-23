from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('', views.admin_dashboard, name='admin_dashboard'),
    
    path('doctors/', views.manage_doctors, name='manage_doctors'),
    path('doctors/add/', views.add_doctor, name='add_doctor'),
    path('doctors/<int:doctor_id>/approve/', views.approve_doctor, name='approve_doctor'),
    path('doctors/<int:doctor_id>/reject/', views.reject_doctor, name='reject_doctor'),
    path('doctors/<int:doctor_id>/edit/', views.edit_doctor, name='edit_doctor'),
    path('doctors/<int:doctor_id>/delete/', views.delete_doctor, name='delete_doctor'),
    
    path('appointments/', views.manage_appointments, name='manage_appointments'),
    path('appointments/add/', views.add_appointment, name='add_appointment'),
    path('appointments/<int:appointment_id>/edit/', views.edit_appointment, name='edit_appointment'),
    path('appointments/<int:appointment_id>/delete/', views.delete_appointment, name='delete_appointment'),
    path('no-show-analytics/', views.no_show_analytics, name='no_show_analytics'),
    path('appointments/<int:appointment_id>/send-reminder/', views.send_reminder, name='send_reminder'),
    path('reminder-logs/', views.reminder_logs, name='reminder_logs'),
    
    path('patients/', views.manage_patients, name='manage_patients'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('patients/<int:user_id>/delete/', views.delete_patient, name='delete_patient'),
    path('similar-patients/<str:patient_email>/', views.similar_patients_view, name='similar_patients'),
    
    path('feedback/', views.manage_feedback, name='manage_feedback'),
    path('feedback/<str:feedback_type>/<int:feedback_id>/approve/', views.approve_feedback, name='approve_feedback'),
    
    path('services/', views.manage_services, name='manage_services'),
    path('services/dental/<int:service_id>/edit/', views.edit_dental_service, name='edit_dental_service'),
    path('services/eye/<int:service_id>/edit/', views.edit_eye_service, name='edit_eye_service'),
    
    path('blog/', views.manage_blog, name='manage_blog'),
    path('blog/add/', views.add_blog, name='add_blog'),
    path('blog/<int:post_id>/edit/', views.edit_blog, name='edit_blog'),
    path('blog/<int:post_id>/delete/', views.delete_blog, name='delete_blog'),
    
    path('gallery/', views.manage_gallery, name='manage_gallery'),
    path('gallery/add/', views.add_gallery, name='add_gallery'),
    path('gallery/<int:image_id>/delete/', views.delete_gallery, name='delete_gallery'),
    
    path('payments/', views.manage_payments, name='manage_payments'),
    path('inquiries/', views.manage_inquiries, name='manage_inquiries'),
    path('settings/', views.admin_settings, name='admin_settings'),

     # Users
    path('users/', views.manage_users, name='manage_users'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),



     # Gallery Categories
    path('gallery/category/add/', views.add_gallery_category, name='add_gallery_category'),
    path('gallery/category/<int:category_id>/edit/', views.edit_gallery_category, name='edit_gallery_category'),
    path('gallery/category/<int:category_id>/delete/', views.delete_gallery_category, name='delete_gallery_category'),

    path('inquiries/<int:inquiry_id>/reply/', views.reply_inquiry, name='reply_inquiry'),
    path('inquiries/<int:inquiry_id>/status/', views.update_inquiry_status, name='update_inquiry_status'),
    path('inquiries/<int:inquiry_id>/delete/', views.delete_inquiry, name='delete_inquiry'),
    path('doctor-rankings/', views.doctor_rankings, name='doctor_rankings'),
]