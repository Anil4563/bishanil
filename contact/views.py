from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactInquiry, ClinicInfo, SupportTicket
import uuid

def contact_page(request):
    """Display contact page with form and clinic info"""
    clinic_info = ClinicInfo.objects.first()
    context = {
        'clinic_info': clinic_info,
    }
    return render(request, 'contact/contact_page.html', context)

def submit_inquiry(request):
    """Handle contact form submission"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        inquiry_type = request.POST.get('inquiry_type')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        preferred_contact = request.POST.get('preferred_contact')
        best_time_to_call = request.POST.get('best_time_to_call', '')
        
        # Save to database
        inquiry = ContactInquiry.objects.create(
            name=name,
            email=email,
            phone=phone,
            inquiry_type=inquiry_type,
            subject=subject,
            message=message,
            preferred_contact=preferred_contact,
            best_time_to_call=best_time_to_call
        )
        
        # Send email notification
        try:
            send_mail(
                f'New Contact Inquiry: {subject}',
                f'Name: {name}\nEmail: {email}\nPhone: {phone}\nType: {inquiry_type}\n\nMessage:\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            
            # Send auto-reply to user
            send_mail(
                'We have received your inquiry - Bishanil Dental & Eye Care',
                f'Dear {name},\n\nThank you for contacting Bishanil Dental & Eye Care. We have received your inquiry and will get back to you within 24 hours.\n\nBest regards,\nBishanil Dental & Eye Care Team',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
            )
        except:
            pass
        
        messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
        return redirect('contact:contact_page')
    
    return redirect('contact:contact_page')

def support_ticket(request):
    """Display support ticket form"""
    clinic_info = ClinicInfo.objects.first()
    context = {
        'clinic_info': clinic_info,
    }
    return render(request, 'contact/support_ticket.html', context)

def submit_support(request):
    """Handle support ticket submission"""
    if request.method == 'POST':
        # Generate unique ticket ID
        ticket_id = f"SKD{str(uuid.uuid4())[:8].upper()}"
        
        patient_name = request.POST.get('patient_name')
        patient_email = request.POST.get('patient_email')
        patient_phone = request.POST.get('patient_phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        priority = request.POST.get('priority')
        
        SupportTicket.objects.create(
            ticket_id=ticket_id,
            patient_name=patient_name,
            patient_email=patient_email,
            patient_phone=patient_phone,
            subject=subject,
            message=message,
            priority=priority
        )
        
        # Send email with ticket ID
        try:
            send_mail(
                f'Support Ticket Created - {ticket_id}',
                f'Dear {patient_name},\n\nYour support ticket has been created.\n\nTicket ID: {ticket_id}\nSubject: {subject}\nPriority: {priority}\n\nWe will respond to your query within 24 hours.\n\nYou can track your ticket status by quoting this ID.\n\nBest regards,\nBishanil Dental & Eye Care Team',
                settings.DEFAULT_FROM_EMAIL,
                [patient_email],
                fail_silently=True,
            )
        except:
            pass
        
        messages.success(request, f'Support ticket created! Your Ticket ID is: {ticket_id}. Please save this for future reference.')
        return redirect('contact:support_ticket')
    
    return redirect('contact:support_ticket')
