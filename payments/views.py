from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import requests
import uuid
from datetime import datetime
from .models import Transaction, PaymentSetting
from appointments.models import Appointment

def initiate_payment(request):
    """Initiate payment for an appointment"""
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        payment_method = request.POST.get('payment_method')
        
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Create transaction record
        transaction = Transaction.objects.create(
            appointment=appointment,
            patient_name=appointment.patient_name,
            patient_email=appointment.patient_email,
            patient_phone=appointment.patient_phone,
            amount=500,  # Default consultation fee
            service_name=appointment.service_name,
            payment_method=payment_method,
            status='pending'
        )
        
        if payment_method == 'khalti':
            return redirect('payments:khalti_verify', transaction_id=transaction.transaction_id)
        elif payment_method == 'esewa':
            return redirect('payments:esewa_success', transaction_id=transaction.transaction_id)
    
    return redirect('appointments:my_appointments')

@login_required
def khalti_verify(request, transaction_id):
    """Verify payment with Khalti"""
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('token')
        amount = data.get('amount')
        
        # Prepare Khalti verification request
        headers = {
            'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'token': token,
            'amount': amount,
        }
        
        try:
            response = requests.post(
                settings.KHALTI_VERIFY_URL,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('state', {}).get('name') == 'Completed':
                    # Update transaction
                    transaction.status = 'completed'
                    transaction.gateway_transaction_id = result.get('idx')
                    transaction.gateway_response = result
                    transaction.paid_at = datetime.now()
                    transaction.save()
                    
                    # Update appointment status
                    if transaction.appointment:
                        transaction.appointment.status = 'confirmed'
                        transaction.appointment.save()
                    
                    return JsonResponse({'success': True, 'transaction_id': transaction.transaction_id})
                else:
                    transaction.status = 'failed'
                    transaction.save()
                    return JsonResponse({'success': False, 'error': 'Payment not completed'})
            else:
                return JsonResponse({'success': False, 'error': 'Verification failed'})
                
        except Exception as e:
            transaction.status = 'failed'
            transaction.save()
            return JsonResponse({'success': False, 'error': str(e)})
    
    context = {
        'transaction': transaction,
        'khalti_public_key': settings.KHALTI_PUBLIC_KEY,
    }
    return render(request, 'payments/khalti_payment.html', context)

def khalti_success(request):
    """Khalti payment success callback"""
    transaction_id = request.GET.get('transaction_id')
    if transaction_id:
        transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
        if transaction.status == 'completed':
            messages.success(request, f'Payment successful! Transaction ID: {transaction.transaction_id}')
            return redirect('payments:payment_status', transaction_id=transaction.transaction_id)
    messages.error(request, 'Payment failed. Please try again.')
    return redirect('appointments:my_appointments')

def khalti_failure(request):
    """Khalti payment failure callback"""
    messages.error(request, 'Payment failed. Please try again.')
    return redirect('appointments:my_appointments')

def esewa_success(request):
    """eSewa payment success callback"""
    # For demo purposes - in production, verify with eSewa
    data = request.GET
    transaction_id = data.get('oid')
    amount = data.get('amt')
    ref_id = data.get('refId')
    
    if transaction_id and ref_id:
        transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
        transaction.status = 'completed'
        transaction.gateway_transaction_id = ref_id
        transaction.paid_at = datetime.now()
        transaction.save()
        
        if transaction.appointment:
            transaction.appointment.status = 'confirmed'
            transaction.appointment.save()
        
        messages.success(request, f'Payment successful! Transaction ID: {transaction.transaction_id}')
        return redirect('payments:payment_status', transaction_id=transaction.transaction_id)
    
    messages.error(request, 'Payment verification failed.')
    return redirect('appointments:my_appointments')

def esewa_failure(request):
    """eSewa payment failure callback"""
    messages.error(request, 'Payment failed. Please try again.')
    return redirect('appointments:my_appointments')

def payment_status(request, transaction_id):
    """View payment status and invoice"""
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
    context = {
        'transaction': transaction,
    }
    return render(request, 'payments/payment_status.html', context)

def download_invoice(request, invoice_number):
    """Download invoice PDF"""
    transaction = get_object_or_404(Transaction, invoice_number=invoice_number)
    
    # For demo - create simple HTML invoice
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Invoice {transaction.invoice_number}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 50px; }}
            .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ color: #26a69a; }}
            .details {{ margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
            .total {{ font-size: 1.2em; font-weight: bold; margin-top: 20px; text-align: right; }}
            .footer {{ text-align: center; margin-top: 50px; font-size: 0.8em; color: #666; }}
        </style>
    </head>
    <body>
        <div class="invoice-box">
            <div class="header">
                <h1>Shree Krishna Dental & Eye Care</h1>
                <p>Kathmandu, Nepal | +977 9800000000</p>
            </div>
            <div class="details">
                <p><strong>Invoice Number:</strong> {transaction.invoice_number}</p>
                <p><strong>Date:</strong> {transaction.paid_at.strftime('%Y-%m-%d') if transaction.paid_at else transaction.created_at.strftime('%Y-%m-%d')}</p>
                <p><strong>Patient Name:</strong> {transaction.patient_name}</p>
                <p><strong>Payment Method:</strong> {transaction.get_payment_method_display()}</p>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{transaction.service_name or 'Consultation Fee'}</td>
                        <td>Rs. {transaction.amount}</td>
                    </tr>
                </tbody>
            </table>
            <div class="total">
                Total: Rs. {transaction.amount}
            </div>
            <div class="footer">
                <p>Thank you for choosing Shree Krishna Dental & Eye Care</p>
                <p>This is a computer-generated invoice. No signature required.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html_content, content_type='text/html')

def latest_transaction(request):
    """Get the latest transaction for the current session"""
    from .models import Transaction
    # Get the most recent pending transaction
    transaction = Transaction.objects.filter(status='pending').last()
    if transaction:
        return JsonResponse({'transaction_id': transaction.transaction_id})
    return JsonResponse({'transaction_id': None})