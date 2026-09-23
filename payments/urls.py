from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('khalti/verify/<str:transaction_id>/', views.khalti_verify, name='khalti_verify'),
    path('khalti/success/', views.khalti_success, name='khalti_success'),
    path('khalti/failure/', views.khalti_failure, name='khalti_failure'),
    path('esewa/success/', views.esewa_success, name='esewa_success'),
    path('esewa/failure/', views.esewa_failure, name='esewa_failure'),
    path('status/<str:transaction_id>/', views.payment_status, name='payment_status'),
    path('invoice/<str:invoice_number>/', views.download_invoice, name='download_invoice'),
    path('latest-transaction/', views.latest_transaction, name='latest_transaction'),
]