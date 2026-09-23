from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ClinicFeedback, DoctorFeedback
from doctors.models import Doctor
from feedback.models import DoctorFeedback

def feedback_page(request):
    """Display feedback form page"""
    doctors = Doctor.objects.filter(is_active=True)
    context = {
        'doctors': doctors,
    }
    return render(request, 'feedback/feedback_form.html', context)

def submit_clinic_feedback(request):
    """Submit feedback for the clinic"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        rating = int(request.POST.get('rating', 5))
        feedback_text = request.POST.get('feedback_text')
        topic = request.POST.get('topic', '')
        
        ClinicFeedback.objects.create(
            name=name,
            email=email,
            phone=phone,
            rating=rating,
            feedback_text=feedback_text,
            topic=topic,
            is_approved=False
        )
        
        messages.success(request, 'Thank you for your feedback! It will be reviewed by our team.')
        return redirect('feedback:feedback_page')
    
    return redirect('feedback:feedback_page')

def submit_doctor_feedback(request, doctor_id):
    """Submit feedback for a specific doctor"""
    doctor = get_object_or_404(Doctor, id=doctor_id, is_active=True)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        rating = int(request.POST.get('rating', 5))
        feedback_text = request.POST.get('feedback_text')
        treatment_received = request.POST.get('treatment_received', '')
        appointment_date = request.POST.get('appointment_date') or None
        
        DoctorFeedback.objects.create(
            name=name,
            email=email,
            phone=phone,
            doctor=doctor,
            rating=rating,
            feedback_text=feedback_text,
            treatment_received=treatment_received,
            appointment_date=appointment_date,
            is_approved=False
        )
        
        messages.success(request, f'Thank you for your feedback about Dr. {doctor.name}! It will be reviewed.')
        return redirect('feedback:feedback_page')
    
    return redirect('feedback:feedback_page')