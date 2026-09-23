from django.shortcuts import render
from doctors.models import Doctor
from contact.models import ContactSettings
from .models import AboutUs, Testimonial, ClinicFeature
from feedback.models import ClinicFeedback, DoctorFeedback
from ml_engine.recommender import get_recommended_doctors


def homepage(request):
    doctors = Doctor.objects.filter(is_active=True, is_featured=True)[:3]
    contact_settings = ContactSettings.objects.first()
    about_us = AboutUs.objects.first()
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    features = ClinicFeature.objects.filter(is_active=True)[:8]
    
    # AI RECOMMENDATION - Top rated doctors
    top_doctors = get_recommended_doctors(limit=3)
    
    # Get approved feedbacks for homepage
    clinic_feedbacks = ClinicFeedback.objects.filter(is_approved=True, show_on_homepage=True)[:4]
    doctor_feedbacks = DoctorFeedback.objects.filter(is_approved=True, show_on_homepage=True)[:4]
    
    context = {
        'site_name': 'Bishanil Dental & Eye Care',
        'teal_color': '#26a69a',
        'doctors': doctors,
        'top_doctors': top_doctors,  # AI powered
        'contact_settings': contact_settings,
        'about_us': about_us,
        'testimonials': testimonials,
        'features': features,
        'clinic_feedbacks': clinic_feedbacks,
        'doctor_feedbacks': doctor_feedbacks,
    }
    return render(request, 'pages/home/home.html', context)