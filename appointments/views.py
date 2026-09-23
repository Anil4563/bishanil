from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Appointment, EmergencyBooking, AppointmentSlot
from dental.models import DentalService
from eyecare.models import EyeService
from doctors.models import Doctor
from datetime import datetime, date
import json

def book_appointment(request):
    """Book a regular appointment"""
    if request.method == 'POST':
        # Get form data
        patient_name = request.POST.get('patient_name')
        patient_email = request.POST.get('patient_email')
        patient_phone = request.POST.get('patient_phone')
        patient_age = request.POST.get('patient_age')
        service_type = request.POST.get('service_type')
        service_id = request.POST.get('service_id')
        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        symptoms = request.POST.get('symptoms', '')
        
        # Get service and doctor objects
        dental_service = None
        eye_service = None
        amount = 500  # Default consultation fee
        
        if service_type == 'dental' and service_id:
            dental_service = get_object_or_404(DentalService, id=service_id)
            amount = float(dental_service.starting_price) if dental_service.starting_price else 500
        elif service_type == 'eye' and service_id:
            eye_service = get_object_or_404(EyeService, id=service_id)
            amount = float(eye_service.starting_price) if eye_service.starting_price else 500
        
        doctor = get_object_or_404(Doctor, id=doctor_id) if doctor_id else None
        
        # Create appointment
        appointment = Appointment.objects.create(
            patient_name=patient_name,
            patient_email=patient_email,
            patient_phone=patient_phone,
            patient_age=patient_age if patient_age else None,
            service_type=service_type,
            dental_service=dental_service,
            eye_service=eye_service,
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            symptoms=symptoms,
            status='pending'  # Set as pending until payment
        )
        
        # Create payment transaction
        from payments.models import Transaction
        transaction = Transaction.objects.create(
            appointment=appointment,
            patient_name=patient_name,
            patient_email=patient_email,
            patient_phone=patient_phone,
            amount=amount,
            service_name=appointment.service_name,
            payment_method='khalti',  # Default to khalti
            status='pending'
        )
        
        # Send email confirmation
        try:
            send_mail(
                f'Appointment Confirmation - {appointment_date}',
                f'Dear {patient_name},\n\nYour appointment has been booked successfully.\n\nDetails:\nDate: {appointment_date}\nTime: {appointment_time}\nService: {appointment.service_name}\nAmount to Pay: Rs. {amount}\n\nPlease complete the payment to confirm your appointment.\n\nThank you for choosing Shree Krishna Dental & Eye Care.',
                settings.DEFAULT_FROM_EMAIL,
                [patient_email],
                fail_silently=True,
            )
        except:
            pass
        
        messages.success(request, f'Your appointment has been booked successfully! Transaction ID: {transaction.transaction_id}')
        return redirect('appointments:booking_success')
    
    # GET request - show booking form
    dental_services = DentalService.objects.filter(is_active=True)
    eye_services = EyeService.objects.filter(is_active=True)
    doctors = Doctor.objects.filter(is_active=True)
    
    context = {
        'dental_services': dental_services,
        'eye_services': eye_services,
        'doctors': doctors,
    }
    return render(request, 'appointments/book_appointment.html', context)


def emergency_booking(request):
    """Book an emergency appointment"""
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name')
        patient_phone = request.POST.get('patient_phone')
        patient_age = request.POST.get('patient_age')
        emergency_type = request.POST.get('emergency_type')
        symptoms = request.POST.get('symptoms')
        preferred_time = request.POST.get('preferred_time')
        
        EmergencyBooking.objects.create(
            patient_name=patient_name,
            patient_phone=patient_phone,
            patient_age=patient_age,
            emergency_type=emergency_type,
            symptoms=symptoms,
            preferred_time=preferred_time
        )
        
        messages.success(request, 'Emergency booking submitted! We will contact you shortly.')
        return redirect('appointments:booking_success')
    
    return render(request, 'appointments/emergency_booking.html')


def booking_success(request):
    """Success page after booking"""
    return render(request, 'appointments/booking_success.html')


def get_available_slots(request):
    """AJAX endpoint to get available time slots for a doctor and date"""
    doctor_id = request.GET.get('doctor_id')
    appointment_date = request.GET.get('date')
    
    if doctor_id and appointment_date:
        slots = AppointmentSlot.objects.filter(
            doctor_id=doctor_id,
            date=appointment_date,
            is_available=True
        )
        
        slots_list = []
        for slot in slots:
            slots_list.append({
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'available': slot.slots_available
            })
        
        return JsonResponse({'slots': slots_list})
    
    return JsonResponse({'slots': []})