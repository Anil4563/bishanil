from django.db import models
from django.contrib.auth.models import User
from appointments.models import Appointment

class Transaction(models.Model):
    """
    Model for all payment transactions
    """
    PAYMENT_METHODS = [
        ('khalti', 'Khalti'),
        ('esewa', 'eSewa'),
        ('cash', 'Cash'),
        ('card', 'Card'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # Transaction Details
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Reference to appointment or service
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    service_name = models.CharField(max_length=200, blank=True)
    
    # Patient Information
    patient_name = models.CharField(max_length=200)
    patient_email = models.EmailField()
    patient_phone = models.CharField(max_length=20)
    
    # Payment Gateway Response
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Invoice
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    invoice_pdf = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount} - {self.status}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            import uuid
            self.transaction_id = f"TXN{str(uuid.uuid4())[:8].upper()}"
        # Only generate invoice number when payment is completed
        if self.status == 'completed' and not self.invoice_number:
            import uuid
            self.invoice_number = f"INV{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)

class PaymentSetting(models.Model):
    """
    Payment gateway settings (can be managed from admin)
    """
    GATEWAY_CHOICES = [
        ('khalti', 'Khalti'),
        ('esewa', 'eSewa'),
    ]
    
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES, unique=True)
    is_enabled = models.BooleanField(default=True)
    secret_key = models.CharField(max_length=200)
    public_key = models.CharField(max_length=200, blank=True)
    merchant_code = models.CharField(max_length=100, blank=True)
    test_mode = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Payment Setting'
        verbose_name_plural = 'Payment Settings'
    
    def __str__(self):
        return f"{self.gateway} - {'Test' if self.test_mode else 'Live'}"