from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import date, timedelta
from appointments.models import Appointment
from doctors.models import Doctor, Prescription
from feedback.models import ClinicFeedback, DoctorFeedback
from payments.models import Transaction
from dental.models import DentalService
from eyecare.models import EyeService
from blog.models import BlogPost
from gallery.models import GalleryImage, GalleryCategory
from contact.models import ContactInquiry, ContactSettings
from homepage.models import AboutUs
from accounts.models import PatientProfile
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse


def is_admin(user):
    return user.is_authenticated and user.is_staff


# ============================================
# LOGIN / LOGOUT
# ============================================

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:admin_dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard:admin_dashboard')
        messages.error(request, 'Invalid credentials or not an admin.')
    return render(request, 'dashboard/admin_login.html')


def admin_logout(request):
    logout(request)
    return redirect('dashboard:admin_login')


# ============================================
# DASHBOARD
# ============================================

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_dashboard(request):
    today = date.today()
    month_start = today.replace(day=1)
    context = {
        'total_doctors': Doctor.objects.count(),
        'pending_doctors': Doctor.objects.filter(is_approved=False).count(),
        'total_patients': User.objects.filter(is_superuser=False, is_staff=False).count(),
        'total_appointments': Appointment.objects.count(),
        'today_appointments': Appointment.objects.filter(appointment_date=today).count(),
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
        'completed_appointments': Appointment.objects.filter(status='completed').count(),
        'total_revenue': Transaction.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
        'monthly_revenue': Transaction.objects.filter(status='completed', created_at__gte=month_start).aggregate(Sum('amount'))['amount__sum'] or 0,
        'pending_feedbacks': ClinicFeedback.objects.filter(is_approved=False).count() + DoctorFeedback.objects.filter(is_approved=False).count(),
        'recent_appointments': Appointment.objects.order_by('-created_at')[:10],
        'recent_patients': User.objects.filter(is_superuser=False, is_staff=False).order_by('-date_joined')[:5],
        'recent_transactions': Transaction.objects.order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


# ============================================
# DOCTORS CRUD
# ============================================

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def manage_doctors(request):
    return render(request, 'dashboard/manage_doctors.html', {
        'pending_doctors': Doctor.objects.filter(is_approved=False).order_by('-registration_date'),
        'approved_doctors': Doctor.objects.filter(is_approved=True).order_by('-approved_date'),
    })


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def approve_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.is_approved = True
    doctor.is_active = True
    doctor.approved_date = timezone.now()
    doctor.approved_by = request.user.username
    doctor.save()
    messages.success(request, f'Dr. {doctor.name} approved!')
    return redirect('dashboard:manage_doctors')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def reject_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.is_approved = False
    doctor.is_active = False
    doctor.save()
    messages.warning(request, f'Dr. {doctor.name} rejected.')
    return redirect('dashboard:manage_doctors')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def add_doctor(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        username = name.lower().replace(' ', '_')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Doctor with this name already exists!')
            return redirect('dashboard:manage_doctors')
        user = User.objects.create(
            username=username, email=email,
            first_name=name.split()[0] if ' ' in name else name,
            last_name=name.split()[-1] if ' ' in name else '',
            password=make_password('doctor123')
        )
        PatientProfile.objects.create(user=user, phone='', address='')
        doctor = Doctor.objects.create(
            user=user, name=name, slug=username,
            specialization_type=request.POST.get('specialization_type'),
            degree=request.POST.get('degree'),
            specialization=request.POST.get('specialization'),
            experience_years=request.POST.get('experience_years'),
            qualifications=request.POST.get('degree') + ' from Medical College',
            expertise=request.POST.get('specialization'),
            languages='English, Nepali',
            consultation_fee=request.POST.get('consultation_fee'),
            availability='Mon-Sat, 9AM-6PM',
            bio=request.POST.get('bio', ''),
            is_active=True, is_approved=True,
            approved_by=request.user.username,
        )
        if request.FILES.get('profile_image'):
            doctor.profile_image = request.FILES['profile_image']
            doctor.save()
        messages.success(request, f'Dr. {name} added successfully! Login: {username} / doctor123')
        return redirect('dashboard:manage_doctors')
    return redirect('dashboard:manage_doctors')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def edit_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        doctor.name = request.POST.get('name')
        doctor.specialization_type = request.POST.get('specialization_type')
        doctor.degree = request.POST.get('degree')
        doctor.specialization = request.POST.get('specialization')
        doctor.experience_years = request.POST.get('experience_years')
        doctor.consultation_fee = request.POST.get('consultation_fee')
        doctor.bio = request.POST.get('bio', '')
        if request.FILES.get('profile_image'):
            doctor.profile_image = request.FILES['profile_image']
        doctor.save()
        messages.success(request, f'Dr. {doctor.name} updated!')
        return redirect('dashboard:manage_doctors')
    return redirect('dashboard:manage_doctors')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    name = doctor.name
    if doctor.user:
        doctor.user.delete()
    doctor.delete()
    messages.success(request, f'Dr. {name} deleted!')
    return redirect('dashboard:manage_doctors')


# ============================================
# APPOINTMENTS CRUD
# ============================================

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def manage_appointments(request):
    from ml_engine.no_show_predictor import predict_no_show, get_model_info

    status_filter = request.GET.get('status', '')
    appointments = Appointment.objects.all().order_by('-appointment_date')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    # Add AI no-show prediction to each appointment
    appointments_with_prediction = []
    for apt in appointments:
        prediction = predict_no_show(apt)
        apt.no_show_prediction = prediction
        appointments_with_prediction.append(apt)

    # Model info for header
    model_info = get_model_info()

    return render(request, 'dashboard/manage_appointments.html', {
        'appointments': appointments_with_prediction,
        'status_filter': status_filter,
        'doctors': Doctor.objects.filter(is_approved=True),
        'model_info': model_info,
    })
    status_filter = request.GET.get('status', '')
    appointments = Appointment.objects.all().order_by('-appointment_date')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    return render(request, 'dashboard/manage_appointments.html', {
        'appointments': appointments,
        'status_filter': status_filter,
        'doctors': Doctor.objects.filter(is_approved=True),
    })


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def add_appointment(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        doctor = Doctor.objects.get(id=doctor_id) if doctor_id else None
        Appointment.objects.create(
            patient_name=request.POST.get('patient_name'),
            patient_email=request.POST.get('patient_email'),
            patient_phone=request.POST.get('patient_phone'),
            patient_age=request.POST.get('patient_age') or None,
            service_type=request.POST.get('service_type'),
            doctor=doctor,
            appointment_date=request.POST.get('appointment_date'),
            appointment_time=request.POST.get('appointment_time'),
            symptoms=request.POST.get('symptoms', ''),
            status='confirmed'
        )
        messages.success(request, 'Appointment created!')
    return redirect('dashboard:manage_appointments')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment.patient_name = request.POST.get('patient_name')
        appointment.patient_email = request.POST.get('patient_email')
        appointment.patient_phone = request.POST.get('patient_phone')
        appointment.appointment_date = request.POST.get('appointment_date')
        appointment.appointment_time = request.POST.get('appointment_time')
        appointment.status = request.POST.get('status')
        appointment.symptoms = request.POST.get('symptoms', '')
        doctor_id = request.POST.get('doctor')
        if doctor_id:
            appointment.doctor = Doctor.objects.get(id=doctor_id)
        appointment.save()
        messages.success(request, 'Appointment updated!')
    return redirect('dashboard:manage_appointments')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def delete_appointment(request, appointment_id):
    Appointment.objects.get(id=appointment_id).delete()
    messages.success(request, 'Appointment deleted!')
    return redirect('dashboard:manage_appointments')


# ============================================
# PATIENTS CRUD
# ============================================

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def manage_patients(request):
    return render(request, 'dashboard/manage_patients.html', {
        'patients': User.objects.filter(is_superuser=False, is_staff=False).order_by('-date_joined')
    })


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def add_patient(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('dashboard:manage_patients')
        user = User.objects.create(
            username=username,
            email=request.POST.get('email'),
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            password=make_password(request.POST.get('password', 'patient123'))
        )
        PatientProfile.objects.create(user=user, phone=request.POST.get('phone', ''), address='')
        messages.success(request, f'Patient created! Login: {username} / patient123')
    return redirect('dashboard:manage_patients')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def delete_patient(request, user_id):
    user = get_object_or_404(User, id=user_id)
    name = user.get_full_name() or user.username
    user.delete()
    messages.success(request, f'Patient {name} deleted!')
    return redirect('dashboard:manage_patients')


# ============================================
# FEEDBACK
# ============================================

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def manage_feedback(request):
    from ml_engine.sentiment import analyze_sentiment, get_sentiment_stats
    
    clinic_feedbacks = ClinicFeedback.objects.all().order_by('-created_at')
    doctor_feedbacks = DoctorFeedback.objects.all().order_by('-created_at')
    
    # Attach sentiment to each clinic feedback
    clinic_fb_list = []
    for fb in clinic_feedbacks:
        fb.sentiment = analyze_sentiment(fb.feedback_text)
        clinic_fb_list.append(fb)
    
    # Attach sentiment to each doctor feedback
    doctor_fb_list = []
    for fb in doctor_feedbacks:
        fb.sentiment = analyze_sentiment(fb.feedback_text)
        doctor_fb_list.append(fb)
    
    # Calculate overall stats
    clinic_stats = get_sentiment_stats(clinic_feedbacks)
    doctor_stats = get_sentiment_stats(doctor_feedbacks)
    
    # Combined stats
    all_feedbacks = list(clinic_feedbacks) + list(doctor_feedbacks)
    overall_stats = get_sentiment_stats(all_feedbacks)
    
    context = {
        'clinic_feedbacks': clinic_fb_list,
        'doctor_feedbacks': doctor_fb_list,
        'clinic_stats': clinic_stats,
        'doctor_stats': doctor_stats,
        'overall_stats': overall_stats,
    }
    return render(request, 'dashboard/manage_feedback.html', context)

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def approve_feedback(request, feedback_type, feedback_id):
    if feedback_type == 'clinic':
        fb = get_object_or_404(ClinicFeedback, id=feedback_id)
    else:
        fb = get_object_or_404(DoctorFeedback, id=feedback_id)
    fb.is_approved = True
    fb.save()
    messages.success(request, 'Feedback approved!')
    return redirect('dashboard:manage_feedback')


# ============================================
# SERVICES
# ============================================

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def manage_services(request):
    return render(request, 'dashboard/manage_services.html', {
        'dental_services': DentalService.objects.all().order_by('order'),
        'eye_services': EyeService.objects.all().order_by('order'),
    })


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def edit_dental_service(request, service_id):
    service = get_object_or_404(DentalService, id=service_id)
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.short_description = request.POST.get('short_description')
        service.full_description = request.POST.get('full_description')
        service.starting_price = request.POST.get('starting_price') or None
        service.is_active = request.POST.get('is_active') == 'on'
        service.save()
        messages.success(request, 'Service updated!')
    return redirect('dashboard:manage_services')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def edit_eye_service(request, service_id):
    service = get_object_or_404(EyeService, id=service_id)
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.short_description = request.POST.get('short_description')
        service.full_description = request.POST.get('full_description')
        service.starting_price = request.POST.get('starting_price') or None
        service.is_active = request.POST.get('is_active') == 'on'
        service.save()
        messages.success(request, 'Service updated!')
    return redirect('dashboard:manage_services')


# ============================================
# BLOG CRUD
# ============================================

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def manage_blog(request):
    return render(request, 'dashboard/manage_blog.html', {'posts': BlogPost.objects.all().order_by('-created_at')})


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def add_blog(request):
    if request.method == 'POST':
        from django.utils.text import slugify
        title = request.POST.get('title')
        slug = slugify(title)
        if BlogPost.objects.filter(slug=slug).exists():
            slug = slug + '-' + str(BlogPost.objects.count() + 1)
        post = BlogPost.objects.create(
            title=title, slug=slug,
            post_type=request.POST.get('post_type'),
            excerpt=request.POST.get('excerpt'),
            content=request.POST.get('content'),
            author_name=request.POST.get('author_name', 'Admin'),
            status=request.POST.get('status', 'published'),
            is_featured=request.POST.get('is_featured') == 'on',
            published_at=timezone.now()
        )
        if request.FILES.get('featured_image'):
            post.featured_image = request.FILES['featured_image']
            post.save()
        messages.success(request, 'Blog post created!')
    return redirect('dashboard:manage_blog')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def edit_blog(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.post_type = request.POST.get('post_type')
        post.excerpt = request.POST.get('excerpt')
        post.content = request.POST.get('content')
        post.status = request.POST.get('status')
        post.is_featured = request.POST.get('is_featured') == 'on'
        if request.FILES.get('featured_image'):
            post.featured_image = request.FILES['featured_image']
        post.save()
        messages.success(request, 'Blog updated!')
    return redirect('dashboard:manage_blog')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def delete_blog(request, post_id):
    BlogPost.objects.get(id=post_id).delete()
    messages.success(request, 'Blog deleted!')
    return redirect('dashboard:manage_blog')


# ============================================
# GALLERY CRUD
# ============================================

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def manage_gallery(request):
    return render(request, 'dashboard/manage_gallery.html', {
        'images': GalleryImage.objects.all().order_by('-date_added'),
        'categories': GalleryCategory.objects.all(),
    })


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def add_gallery(request):
    if request.method == 'POST':
        category = GalleryCategory.objects.get(id=request.POST.get('category'))
        image = GalleryImage.objects.create(
            title=request.POST.get('title'),
            category=category,
            description=request.POST.get('description', ''),
            is_active=True
        )
        if request.FILES.get('image'):
            image.image = request.FILES['image']
            image.save()
        messages.success(request, 'Image added!')
    return redirect('dashboard:manage_gallery')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def delete_gallery(request, image_id):
    GalleryImage.objects.get(id=image_id).delete()
    messages.success(request, 'Image deleted!')
    return redirect('dashboard:manage_gallery')


# ============================================
# PAYMENTS & INQUIRIES
# ============================================

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def manage_payments(request):
    transactions = Transaction.objects.all().order_by('-created_at')
    return render(request, 'dashboard/manage_payments.html', {
        'transactions': transactions,
        'total_revenue': transactions.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
    })


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def manage_inquiries(request):
    return render(request, 'dashboard/manage_inquiries.html', {
        'inquiries': ContactInquiry.objects.all().order_by('-created_at')
    })


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_settings(request):
    return render(request, 'dashboard/admin_settings.html', {
        'contact': ContactSettings.objects.first(),
        'about': AboutUs.objects.first(),
    })

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def manage_users(request):
    """Manage all users (admin, staff, patients)"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'dashboard/manage_users.html', {'users': users})


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def add_user(request):
    """Add new user"""
    if request.method == 'POST':
        username = request.POST.get('username')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('dashboard:manage_users')
        
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        
        user = User.objects.create(
            username=username,
            email=request.POST.get('email'),
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            password=make_password(request.POST.get('password', 'user123')),
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        
        # Create profile for non-staff users
        if not is_staff:
            PatientProfile.objects.create(user=user, phone=request.POST.get('phone', ''), address='')
        
        messages.success(request, f'User {username} created!')
    return redirect('dashboard:manage_users')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def edit_user(request, user_id):
    """Edit user"""
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'
        user.save()
        
        if user.profile and request.POST.get('phone'):
            user.profile.phone = request.POST.get('phone')
            user.profile.save()
        
        messages.success(request, f'User {user.username} updated!')
    return redirect('dashboard:manage_users')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def delete_user(request, user_id):
    """Delete user"""
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "You can't delete yourself!")
        return redirect('dashboard:manage_users')
    name = user.username
    user.delete()
    messages.success(request, f'User {name} deleted!')
    return redirect('dashboard:manage_users')

# ============================================
# GALLERY CATEGORIES CRUD
# ============================================

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def add_gallery_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        category_type = request.POST.get('category_type')
        description = request.POST.get('description', '')
        icon_class = request.POST.get('icon_class', 'fas fa-images')
        order = request.POST.get('order', 0)

        if GalleryCategory.objects.filter(slug=slug).exists():
            messages.error(request, 'Category with this slug already exists!')
            return redirect('dashboard:manage_gallery')

        GalleryCategory.objects.create(
            name=name,
            slug=slug,
            category_type=category_type,
            description=description,
            icon_class=icon_class,
            order=order,
            is_active=True
        )
        messages.success(request, f'Category "{name}" created!')
    return redirect('dashboard:manage_gallery')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def edit_gallery_category(request, category_id):
    category = get_object_or_404(GalleryCategory, id=category_id)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.slug = request.POST.get('slug')
        category.category_type = request.POST.get('category_type')
        category.description = request.POST.get('description', '')
        category.icon_class = request.POST.get('icon_class', 'fas fa-images')
        category.order = request.POST.get('order', 0)
        category.is_active = request.POST.get('is_active') == 'on'
        category.save()
        messages.success(request, f'Category "{category.name}" updated!')
    return redirect('dashboard:manage_gallery')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def delete_gallery_category(request, category_id):
    category = get_object_or_404(GalleryCategory, id=category_id)
    name = category.name
    category.delete()
    messages.success(request, f'Category "{name}" deleted!')
    return redirect('dashboard:manage_gallery')

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def reply_inquiry(request, inquiry_id):
    """Reply to a contact inquiry via email"""
    inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)
    
    if request.method == 'POST':
        reply_message = request.POST.get('reply_message', '')
        
        if reply_message:
            try:
                # Send email reply
                send_mail(
                    subject=f'Re: {inquiry.subject} - Bishanil Dental',
                    message=reply_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[inquiry.email],
                    fail_silently=False,
                )
                
                # Update inquiry status
                inquiry.status = 'replied'
                inquiry.admin_notes = reply_message
                inquiry.save()
                
                messages.success(request, f'Reply sent to {inquiry.email}!')
            except Exception as e:
                messages.error(request, f'Error sending email: {str(e)}')
        
        return redirect('dashboard:manage_inquiries')
    
    return redirect('dashboard:manage_inquiries')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def update_inquiry_status(request, inquiry_id):
    """Update inquiry status"""
    inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)
    if request.method == 'POST':
        inquiry.status = request.POST.get('status', inquiry.status)
        inquiry.save()
        messages.success(request, f'Inquiry status updated to {inquiry.status}!')
    return redirect('dashboard:manage_inquiries')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def delete_inquiry(request, inquiry_id):
    """Delete an inquiry"""
    inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)
    inquiry.delete()
    messages.success(request, 'Inquiry deleted!')
    return redirect('dashboard:manage_inquiries')

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def doctor_rankings(request):
    """AI-powered doctor rankings"""
    from ml_engine.recommender import get_all_doctor_rankings
    
    rankings = get_all_doctor_rankings()
    
    context = {
        'rankings': rankings,
    }
    return render(request, 'dashboard/doctor_rankings.html', context)

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def similar_patients_view(request, patient_email):
    """AJAX endpoint: Find similar patients for a given patient"""
    from accounts.models import PatientProfile, MedicalHistory
    from ml_engine.similar_patients import find_similar_patients, get_similarity_reason

    try:
        # Find the patient profile by email
        profile = PatientProfile.objects.select_related('user').get(user__email=patient_email)

        # Find similar patients
        similar = find_similar_patients(profile, k=5)

        # Build response data
        results = []
        try:
            target_history = MedicalHistory.objects.get(patient=profile)
        except MedicalHistory.DoesNotExist:
            target_history = None

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
        return JsonResponse({'success': False, 'error': 'Patient profile not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def no_show_analytics(request):
    """No-Show Prediction Analytics Dashboard"""
    from ml_engine.no_show_predictor import train_model, predict_no_show, get_model_info
    from appointments.models import Appointment

    # Train model and get info
    model, scaler, model_info = train_model()

    # Get all upcoming appointments
    upcoming = Appointment.objects.filter(
        status__in=['pending', 'confirmed']
    ).order_by('appointment_date')

    # Predict for each upcoming appointment
    upcoming_predictions = []
    high_risk = 0
    medium_risk = 0
    low_risk = 0

    for apt in upcoming:
        pred = predict_no_show(apt)
        apt.prediction = pred
        upcoming_predictions.append(apt)

        if pred['model_ready']:
            if pred['risk_level'] == 'high':
                high_risk += 1
            elif pred['risk_level'] == 'medium':
                medium_risk += 1
            else:
                low_risk += 1

    # Historical stats
    total = Appointment.objects.filter(attendance_status__in=['came', 'not_came']).count()
    came = Appointment.objects.filter(attendance_status='came').count()
    not_came = Appointment.objects.filter(attendance_status='not_came').count()

    attendance_rate = round((came / total * 100), 1) if total > 0 else 0
    no_show_rate = round((not_came / total * 100), 1) if total > 0 else 0

    context = {
        'model_info': model_info,
        'upcoming_predictions': upcoming_predictions[:20],
        'high_risk': high_risk,
        'medium_risk': medium_risk,
        'low_risk': low_risk,
        'total_upcoming': upcoming.count(),
        'total_historical': total,
        'came': came,
        'not_came': not_came,
        'attendance_rate': attendance_rate,
        'no_show_rate': no_show_rate,
    }
    return render(request, 'dashboard/no_show_analytics.html', context)

from django.core.mail import send_mail
from django.conf import settings
from appointments.models import AppointmentReminder
from ml_engine.reminder_generator import generate_reminder_message
from ml_engine.no_show_predictor import predict_no_show


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def send_reminder(request, appointment_id):
    """Send a reminder for an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        reminder_type = request.POST.get('reminder_type', 'email')
        custom_message = request.POST.get('message', '').strip()
        
        # Get AI prediction for risk level
        prediction = predict_no_show(appointment)
        risk_level = prediction.get('risk_level', 'medium') if prediction.get('model_ready') else 'medium'
        probability = prediction.get('probability', 0)
        
        # Generate message if not custom
        if custom_message:
            subject = f"Appointment Reminder - {appointment.appointment_date}"
            message = custom_message
        else:
            generated = generate_reminder_message(appointment, risk_level, probability)
            subject = generated['subject']
            message = generated['message']
        
        # Send email
        email_sent = False
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[appointment.patient_email],
                fail_silently=True,
            )
            email_sent = True
        except Exception as e:
            print(f"Email error: {e}")
        
        # Log reminder
        reminder = AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_type=reminder_type,
            message=message,
            status='sent' if email_sent else 'failed',
            risk_level=risk_level,
            no_show_probability=probability,
            sent_by=request.user.username,
        )
        
        if email_sent:
            messages.success(request, f'Reminder sent to {appointment.patient_name}! (Risk: {risk_level.upper()}, {probability}% no-show)')
        else:
            messages.warning(request, f'Reminder logged but email failed. Check console.')
    
    return redirect('dashboard:manage_appointments')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(is_admin, login_url='/admin-panel/login/')
def reminder_logs(request):
    """View all reminder logs"""
    reminders = AppointmentReminder.objects.all().order_by('-sent_at')
    
    context = {
        'reminders': reminders,
        'total': reminders.count(),
        'email_count': reminders.filter(reminder_type='email').count(),
        'high_risk_count': reminders.filter(risk_level='high').count(),
    }
    return render(request, 'dashboard/reminder_logs.html', context)
