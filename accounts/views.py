from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from appointments.models import Appointment
from django.contrib.auth import update_session_auth_hash, logout 
from .models import PatientProfile, MedicalHistory
from doctors.models import Prescription
from payments.models import Transaction

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now login.')
            return redirect('accounts:login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    """Patient dashboard"""
    try:
        profile = request.user.profile
    except:
        profile = PatientProfile.objects.create(user=request.user)
    
    appointments = Appointment.objects.filter(
        patient_email=request.user.email
    ).order_by('-appointment_date', '-appointment_time')
    
    upcoming_appointments = appointments.filter(status='confirmed')[:3]
    past_appointments = appointments.filter(status='completed')[:3]
    
    # Get or create medical history
    medical_history, created = MedicalHistory.objects.get_or_create(patient=profile)
    
    # Get prescriptions for this patient
    from doctors.models import Prescription
    prescriptions = Prescription.objects.filter(patient_email=request.user.email).order_by('-created_at')[:5]
    
    # Get bills/transactions for this patient
    bills = Transaction.objects.filter(patient_email=request.user.email).order_by('-created_at')[:10]
    
    context = {
        'appointments': appointments,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'total_appointments': appointments.count(),
        'user': request.user,
        'medical_history': medical_history,
        'prescriptions': prescriptions,
        'bills': bills,
    }
    return render(request, 'accounts/dashboard.html', context)

def custom_logout(request):
    logout(request)
    return redirect('/')  

@login_required
def profile(request):
    """Update user profile"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def my_appointments(request):
    """View all appointments for the patient"""
    appointments = Appointment.objects.filter(
        patient_email=request.user.email
    ).exclude(notes__icontains='Follow-up').order_by('-appointment_date', '-appointment_time')
    
    followup_appointments = Appointment.objects.filter(
        patient_email=request.user.email,
        notes__icontains='Follow-up'
    ).order_by('-appointment_date', '-appointment_time')
    
    context = {
        'appointments': appointments,
        'followup_appointments': followup_appointments,
        'active_tab': 'appointments',
    }
    return render(request, 'accounts/my_appointments.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient_email=request.user.email)
    
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.attendance_status = 'not_came'
        appointment.save()
        messages.success(request, f'Your appointment on {appointment.appointment_date} has been cancelled.')
        return redirect('accounts:my_appointments')
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'accounts/cancel_appointment.html', context)

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {'form': form}
    return render(request, 'accounts/change_password.html', context)

@login_required
def reschedule_appointment(request, appointment_id):
    """Request to reschedule an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient_email=request.user.email)
    
    if request.method == 'POST':
        new_date = request.POST.get('new_date')
        new_time = request.POST.get('new_time')
        reason = request.POST.get('reason', '')
        
        # Save reschedule request
        appointment.reschedule_requested = True
        appointment.reschedule_request_date = new_date
        appointment.reschedule_request_time = new_time
        appointment.reschedule_reason = reason
        appointment.save()
        
        messages.success(request, f'Reschedule request submitted for {new_date} at {new_time}. We will confirm soon.')
        return redirect('accounts:my_appointments')
    
    return redirect('accounts:my_appointments')

@login_required
def update_medical_history(request):
    if request.method == 'POST':
        profile = request.user.profile
        medical_history, created = MedicalHistory.objects.get_or_create(patient=profile)
        
        medical_history.blood_pressure = request.POST.get('blood_pressure', '')
        medical_history.diabetes = request.POST.get('diabetes') == 'on'
        medical_history.thyroid = request.POST.get('thyroid') == 'on'
        medical_history.asthma = request.POST.get('asthma') == 'on'
        medical_history.heart_disease = request.POST.get('heart_disease') == 'on'
        medical_history.allergies = request.POST.get('allergies', '')
        medical_history.current_medications = request.POST.get('current_medications', '')
        medical_history.past_surgeries = request.POST.get('past_surgeries', '')
        medical_history.family_history = request.POST.get('family_history', '')
        medical_history.last_dental_visit = request.POST.get('last_dental_visit') or None
        medical_history.dental_issues = request.POST.get('dental_issues', '')
        medical_history.last_eye_exam = request.POST.get('last_eye_exam') or None
        medical_history.glasses_contact_lens = request.POST.get('glasses_contact_lens', '')
        medical_history.eye_issues = request.POST.get('eye_issues', '')
        
        medical_history.save()
        messages.success(request, 'Medical history updated successfully!')
        return redirect('accounts:dashboard')
    
    return redirect('accounts:dashboard')