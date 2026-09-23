from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Doctor, DoctorSchedule, DoctorReview, Prescription
from .forms import DoctorRegistrationForm
from feedback.models import DoctorFeedback
from accounts.models import PatientProfile
from appointments.models import Appointment

# ============================================
# PUBLIC VIEWS
# ============================================

def doctor_list(request):
    """Display all doctors"""
    dental_doctors = Doctor.objects.filter(specialization_type='dental', is_active=True, is_approved=True)
    eye_doctors = Doctor.objects.filter(specialization_type='eye', is_active=True, is_approved=True)
    featured_doctors = Doctor.objects.filter(is_featured=True, is_active=True, is_approved=True)
    
    context = {
        'dental_doctors': dental_doctors,
        'eye_doctors': eye_doctors,
        'featured_doctors': featured_doctors,
    }
    return render(request, 'doctors/doctor_list.html', context)
def doctor_detail(request, slug):
    """Display detailed information about a specific doctor"""
    from ml_engine.recommender import get_similar_doctors
    
    doctor = get_object_or_404(Doctor, slug=slug, is_active=True)
    schedule = doctor.schedule.filter(is_available=True)
    reviews = doctor.reviews.filter(is_approved=True)[:5]
    
    # Get approved feedback for this doctor
    feedbacks = DoctorFeedback.objects.filter(
        doctor=doctor, 
        is_approved=True
    ).order_by('-created_at')[:10]
    
    # AI RECOMMENDATION - Similar doctors
    similar_doctors = get_similar_doctors(doctor, limit=3)
    
    # Calculate average rating
    avg_rating = 0
    if reviews:
        total = sum(r.rating for r in reviews)
        avg_rating = round(total / reviews.count(), 1)
    
    # Calculate average feedback rating
    feedback_avg = 0
    if feedbacks:
        total_fb = sum(f.rating for f in feedbacks)
        feedback_avg = round(total_fb / feedbacks.count(), 1)
    
    context = {
        'doctor': doctor,
        'schedule': schedule,
        'reviews': reviews,
        'feedbacks': feedbacks,
        'similar_doctors': similar_doctors,  # AI RECOMMENDATIONS
        'avg_rating': avg_rating,
        'feedback_avg': feedback_avg,
        'total_reviews': reviews.count(),
        'total_feedbacks': feedbacks.count(),
    }
    return render(request, 'doctors/doctor_detail.html', context)

# ============================================
# DOCTOR REGISTRATION & LOGIN
# ============================================

def doctor_register(request):
    """Doctor registration with admin approval"""
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create User account for doctor
            username = form.cleaned_data['name'].lower().replace(' ', '_')
            email = f"{username}@bishanildental.com"
            password = form.cleaned_data['password']
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please contact admin.')
                return redirect('doctors:doctor_register')
            
            # Create User
            user = User.objects.create(
                username=username,
                email=email,
                first_name=form.cleaned_data['name'].split()[0] if ' ' in form.cleaned_data['name'] else form.cleaned_data['name'],
                last_name=form.cleaned_data['name'].split()[-1] if ' ' in form.cleaned_data['name'] else '',
                password=make_password(password)
            )
            
            # Create Profile
            PatientProfile.objects.create(
                user=user,
                phone='',
                address=''
            )
            
            # Create Doctor profile (pending approval)
            doctor = form.save(commit=False)
            doctor.slug = username
            doctor.is_active = True
            doctor.is_approved = False
            doctor.user = user
            doctor.save()
            
            messages.success(request, 'Registration submitted successfully! Your profile will be reviewed by admin.')
            return redirect('doctors:doctor_login')
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'doctors/doctor_register.html', {'form': form})

def doctor_login(request):
    """Doctor login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is a doctor
            try:
                doctor = Doctor.objects.get(user=user)
                if doctor.is_approved:
                    login(request, user)
                    messages.success(request, f'Welcome back Dr. {doctor.name}!')
                    return redirect('doctors:doctor_dashboard')
                else:
                    messages.warning(request, 'Your account is pending admin approval. Please wait.')
            except Doctor.DoesNotExist:
                messages.error(request, 'This account is not registered as a doctor.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'doctors/doctor_login.html')

# ============================================
# DOCTOR DASHBOARD
# ============================================

@login_required
def doctor_dashboard(request):
    """Doctor dashboard view - only for approved doctors"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        if not doctor.is_approved:
            messages.warning(request, 'Your account is pending approval.')
            return redirect('doctors:doctor_login')
        
        # Handle profile update
        if request.method == 'POST':
            doctor.name = request.POST.get('name', doctor.name)
            doctor.specialization = request.POST.get('specialization', doctor.specialization)
            doctor.experience_years = request.POST.get('experience_years', doctor.experience_years)
            doctor.consultation_fee = request.POST.get('consultation_fee', doctor.consultation_fee)
            doctor.qualifications = request.POST.get('qualifications', doctor.qualifications)
            doctor.expertise = request.POST.get('expertise', doctor.expertise)
            doctor.bio = request.POST.get('bio', doctor.bio)
            
            if request.FILES.get('profile_image'):
                doctor.profile_image = request.FILES['profile_image']
            
            doctor.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('doctors:doctor_dashboard')
        
        # Get all appointments for this doctor
        all_appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')
        recent_appointments = all_appointments[:10]
        
        # Get unique patients
        patients = []
        patient_emails = all_appointments.values_list('patient_email', flat=True).distinct()
        for email in patient_emails:
            patient_appointments = all_appointments.filter(patient_email=email)
            patients.append({
                'patient_name': patient_appointments.first().patient_name,
                'patient_email': email,
                'patient_phone': patient_appointments.first().patient_phone,
                'appointment_count': patient_appointments.count()
            })
        
        # Get prescriptions
        prescriptions = Prescription.objects.filter(doctor=doctor).order_by('-created_at')
        
        context = {
            'doctor': doctor,
            'appointments': recent_appointments,
            'all_appointments': all_appointments,
            'patients': patients,
            'prescriptions': prescriptions,
            'appointment_count': all_appointments.count(),
            'patient_count': len(patients),
            'prescription_count': prescriptions.count(),
        }
        return render(request, 'doctors/doctor_dashboard.html', context)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('doctors:doctor_login')

# ============================================
# PRESCRIPTION MANAGEMENT
# ============================================

@login_required
def give_prescription(request):
    """Doctor gives prescription to patient"""
    if request.method == 'POST':
        try:
            doctor = Doctor.objects.get(user=request.user)
            if not doctor.is_approved:
                return JsonResponse({'error': 'Doctor not approved'}, status=403)
            
            data = json.loads(request.body)
            
            prescription = Prescription.objects.create(
                doctor=doctor,
                patient_name=data.get('patient_name'),
                patient_email=data.get('patient_email'),
                patient_phone=data.get('patient_phone', ''),
                diagnosis=data.get('diagnosis'),
                medicines=data.get('medicines'),
                instructions=data.get('instructions', ''),
                follow_up_required=data.get('follow_up_required', False),
                follow_up_date=data.get('follow_up_date') or None
            )
            
            return JsonResponse({
                'success': True,
                'prescription_id': prescription.id,
                'message': 'Prescription added successfully!'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def view_prescription(request, prescription_id):
    """View prescription details"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        prescription = Prescription.objects.get(id=prescription_id, doctor=doctor)
        
        data = {
            'id': prescription.id,
            'patient_name': prescription.patient_name,
            'patient_email': prescription.patient_email,
            'patient_phone': prescription.patient_phone,
            'diagnosis': prescription.diagnosis,
            'medicines': prescription.medicines,
            'instructions': prescription.instructions,
            'follow_up_required': prescription.follow_up_required,
            'follow_up_date': prescription.follow_up_date.strftime('%Y-%m-%d') if prescription.follow_up_date else '',
            'created_at': prescription.created_at.strftime('%d %B, %Y'),
            'doctor_name': doctor.name,
            'doctor_specialization': doctor.specialization
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

def print_prescription(request, prescription_id):
    """Generate printable prescription HTML"""
    try:
        prescription = Prescription.objects.get(id=prescription_id)
        doctor = prescription.doctor
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prescription - {prescription.patient_name}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 40px;
                    margin: 0;
                }}
                .prescription-box {{
                    max-width: 800px;
                    margin: 0 auto;
                    border: 1px solid #ddd;
                    padding: 30px;
                    border-radius: 10px;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #26a69a;
                    padding-bottom: 20px;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    color: #26a69a;
                    margin: 0;
                }}
                .doctor-info {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .patient-info {{
                    background: #f5f5f5;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .section {{
                    margin-bottom: 20px;
                }}
                .section h3 {{
                    color: #26a69a;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 5px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
                @media print {{
                    body {{
                        padding: 0;
                    }}
                    .no-print {{
                        display: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="prescription-box">
                <div class="header">
                    <h1>Bishanil Dental & Eye Care</h1>
                    <p>Kathmandu, Nepal | Tel: +977 9800000000</p>
                </div>
                
                <div class="doctor-info">
                    <strong>Dr. {doctor.name}</strong><br>
                    {doctor.specialization}<br>
                    Regd. No: SKD/DOCT/{doctor.id}
                </div>
                
                <div class="patient-info">
                    <strong>Patient Name:</strong> {prescription.patient_name}<br>
                    <strong>Date:</strong> {prescription.created_at.strftime('%d %B, %Y')}
                </div>
                
                <div class="section">
                    <h3>Diagnosis</h3>
                    <p>{prescription.diagnosis}</p>
                </div>
                
                <div class="section">
                    <h3>Medicines Prescribed</h3>
                    <p style="white-space: pre-line;">{prescription.medicines}</p>
                </div>
                
                <div class="section">
                    <h3>Instructions</h3>
                    <p>{prescription.instructions or 'No additional instructions'}</p>
                </div>
                
                <div class="section">
                    <h3>Follow-up</h3>
                    <p>{'Follow-up required on ' + prescription.follow_up_date.strftime('%d %B, %Y') if prescription.follow_up_required and prescription.follow_up_date else 'No follow-up required'}</p>
                </div>
                
                <div class="footer">
                    <p>This is a computer generated prescription. No signature required.</p>
                    <p>For any queries, please contact our clinic.</p>
                </div>
            </div>
            
            <div class="no-print" style="text-align: center; margin-top: 20px;">
                <button onclick="window.print()" style="padding: 10px 20px; background: #26a69a; color: white; border: none; border-radius: 5px; cursor: pointer;">Print Prescription</button>
                <button onclick="window.close()" style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;">Close</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html_content)
    except Prescription.DoesNotExist:
        return HttpResponse("Prescription not found", status=404)

# ============================================
# PATIENT MANAGEMENT
# ============================================

@login_required
def view_patient_details(request, patient_email):
    """View complete patient details including appointments and prescriptions"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        if not doctor.is_approved:
            return JsonResponse({'error': 'Doctor not approved'}, status=403)
        
        # Get patient appointments
        appointments = Appointment.objects.filter(
            doctor=doctor,
            patient_email=patient_email
        ).order_by('-appointment_date')
        
        # Get patient prescriptions
        prescriptions = Prescription.objects.filter(
            doctor=doctor,
            patient_email=patient_email
        ).order_by('-created_at')
        
        # Get patient info from first appointment
        patient_info = {}
        if appointments.exists():
            first = appointments.first()
            patient_info = {
                'name': first.patient_name,
                'email': first.patient_email,
                'phone': first.patient_phone,
                'age': first.patient_age if first.patient_age else 'Not provided'
            }
        else:
            # If no appointments, try to get from prescriptions
            if prescriptions.exists():
                first_pres = prescriptions.first()
                patient_info = {
                    'name': first_pres.patient_name,
                    'email': first_pres.patient_email,
                    'phone': first_pres.patient_phone if first_pres.patient_phone else 'Not provided',
                    'age': 'Not provided'
                }
            else:
                patient_info = {
                    'name': 'Unknown',
                    'email': patient_email,
                    'phone': 'Not provided',
                    'age': 'Not provided'
                }
        
        # Prepare appointment data
        appointments_data = []
        for apt in appointments:
            appointments_data.append({
                'date': apt.appointment_date.strftime('%d %B, %Y'),
                'time': apt.appointment_time.strftime('%I:%M %p'),
                'service': apt.service_name,
                'status': apt.get_status_display(),
                'symptoms': apt.symptoms if apt.symptoms else 'No symptoms recorded'
            })
        
        # Prepare prescription data
        prescriptions_data = []
        for pres in prescriptions:
            prescriptions_data.append({
                'id': pres.id,
                'date': pres.created_at.strftime('%d %B, %Y'),
                'diagnosis': pres.diagnosis,
                'medicines': pres.medicines,
                'instructions': pres.instructions if pres.instructions else 'No instructions',
                'follow_up': pres.follow_up_date.strftime('%d %B, %Y') if pres.follow_up_date else 'None'
            })
        
        return JsonResponse({
            'success': True,
            'patient': patient_info,
            'appointments': appointments_data,
            'prescriptions': prescriptions_data,
            'total_appointments': appointments.count(),
            'total_prescriptions': prescriptions.count()
        })
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    """View complete patient details including appointments and prescriptions"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        if not doctor.is_approved:
            return JsonResponse({'error': 'Doctor not approved'}, status=403)
        
        # Get patient appointments
        appointments = Appointment.objects.filter(
            doctor=doctor,
            patient_email=patient_email
        ).order_by('-appointment_date')
        
        # Get patient prescriptions
        prescriptions = Prescription.objects.filter(
            doctor=doctor,
            patient_email=patient_email
        ).order_by('-created_at')
        
        # Get patient info from first appointment
        patient_info = {}
        if appointments.exists():
            first = appointments.first()
            patient_info = {
                'name': first.patient_name,
                'email': first.patient_email,
                'phone': first.patient_phone,
                'age': first.patient_age
            }
        
        # Prepare appointment data
        appointments_data = []
        for apt in appointments:
            appointments_data.append({
                'date': apt.appointment_date.strftime('%d %B, %Y'),
                'time': apt.appointment_time.strftime('%I:%M %p'),
                'service': apt.service_name,
                'status': apt.get_status_display(),
                'symptoms': apt.symptoms
            })
        
        # Prepare prescription data
        prescriptions_data = []
        for pres in prescriptions:
            prescriptions_data.append({
                'id': pres.id,
                'date': pres.created_at.strftime('%d %B, %Y'),
                'diagnosis': pres.diagnosis,
                'medicines': pres.medicines,
                'instructions': pres.instructions,
                'follow_up': pres.follow_up_date.strftime('%d %B, %Y') if pres.follow_up_date else 'None'
            })
        
        return JsonResponse({
            'success': True,
            'patient': patient_info,
            'appointments': appointments_data,
            'prescriptions': prescriptions_data,
            'total_appointments': appointments.count(),
            'total_prescriptions': prescriptions.count()
        })
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)

@login_required(login_url='/doctors/login/')
def similar_patients_doctor(request, patient_email):
    """AJAX endpoint: Find similar patients (for doctors)"""
    from accounts.models import PatientProfile, MedicalHistory
    from ml_engine.similar_patients import find_similar_patients, get_similarity_reason

    try:
        doctor = Doctor.objects.get(user=request.user)
        if not doctor.is_approved:
            return JsonResponse({'error': 'Doctor not approved'}, status=403)

        profile = PatientProfile.objects.select_related('user').get(user__email=patient_email)
        similar = find_similar_patients(profile, k=5)

        # Get target history for reason comparison
        try:
            target_history = MedicalHistory.objects.get(patient=profile)
        except MedicalHistory.DoesNotExist:
            target_history = None

        results = []
        for item in similar:
            patient = item['patient']
            history = item['medical_history']

            reason = 'Similar overall profile'
            if target_history:
                try:
                    reason = get_similarity_reason(target_history, history)
                except:
                    pass

            results.append({
                'name': patient.user.get_full_name() or patient.user.username,
                'email': patient.user.email,
                'phone': patient.phone or '-',
                'blood_group': patient.blood_group or '-',
                'similarity': item['similarity'],
                'reason': reason,
                'diabetes': history.diabetes,
                'thyroid': history.thyroid,
                'asthma': history.asthma,
                'heart_disease': history.heart_disease,
                'blood_pressure': history.blood_pressure or '-',
                'allergies': history.allergies or '-',
            })

        return JsonResponse({'success': True, 'patients': results})

    except PatientProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Patient not found'}, status=404)
    except Doctor.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Doctor not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
