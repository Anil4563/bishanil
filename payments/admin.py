from django.contrib import admin
from .models import Transaction, PaymentSetting

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'patient_name', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['transaction_id', 'patient_name', 'patient_email', 'patient_phone']
    list_editable = ['status']
    readonly_fields = ['transaction_id', 'invoice_number', 'gateway_response', 'created_at']
    fieldsets = (
        ('Transaction Details', {
            'fields': ('transaction_id', 'payment_method', 'amount', 'status')
        }),
        ('Patient Information', {
            'fields': ('patient_name', 'patient_email', 'patient_phone')
        }),
        ('Appointment Reference', {
            'fields': ('appointment', 'service_name')
        }),
        ('Gateway Response', {
            'fields': ('gateway_transaction_id', 'gateway_response')
        }),
        ('Invoice', {
            'fields': ('invoice_number', 'invoice_pdf')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'paid_at')
        }),
    )

@admin.register(PaymentSetting)
class PaymentSettingAdmin(admin.ModelAdmin):
    list_display = ['gateway', 'is_enabled', 'test_mode']
    list_editable = ['is_enabled', 'test_mode']
    fieldsets = (
        ('Gateway Settings', {
            'fields': ('gateway', 'is_enabled', 'test_mode')
        }),
        ('API Keys', {
            'fields': ('secret_key', 'public_key', 'merchant_code')
        }),
    )