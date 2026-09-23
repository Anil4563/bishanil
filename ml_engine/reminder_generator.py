"""
AI-Powered Reminder Generator
Creates personalized reminder messages based on no-show risk level.
"""


def generate_reminder_message(appointment, risk_level='medium', probability=0):
    """
    Generate an AI-powered reminder message based on risk level.
    
    Args:
        appointment: Appointment instance
        risk_level: 'low', 'medium', or 'high'
        probability: no-show probability (0-100)
    
    Returns:
        dict with 'subject' and 'message'
    """
    patient_name = appointment.patient_name.split()[0] if appointment.patient_name else 'Patient'
    date_str = appointment.appointment_date.strftime('%A, %d %B %Y')
    time_str = appointment.appointment_time.strftime('%I:%M %p')
    doctor_name = f"Dr. {appointment.doctor.name}" if appointment.doctor else "our specialist"
    service = appointment.service_name or "consultation"
    
    # Base message parts
    clinic_name = "Bishanil Dental & Eye Care"
    clinic_phone = "+977 9800000000"
    clinic_address = "Putalisadak, Kathmandu"
    
    if risk_level == 'high':
        subject = f"⚠️ URGENT: Confirm Your Appointment - {date_str}"
        message = f"""Dear {patient_name},

⚠️ URGENT REMINDER

Your appointment is scheduled for:
📅 Date: {date_str}
⏰ Time: {time_str}
👨‍⚕️ Doctor: {doctor_name}
🏥 Service: {service}

We noticed you may have missed appointments before. This is a friendly but important reminder.

To confirm your appointment, please:
📞 Call us: {clinic_phone}
💬 WhatsApp: {clinic_phone}

If you cannot attend, please let us know at least 24 hours in advance so we can reschedule.

Your health is important — we look forward to seeing you!

Warm regards,
{clinic_name}
{clinic_address}
"""
    
    elif risk_level == 'medium':
        subject = f"Reminder: Your Appointment on {date_str}"
        message = f"""Dear {patient_name},

This is a friendly reminder about your upcoming appointment:

📅 Date: {date_str}
⏰ Time: {time_str}
👨‍⚕️ Doctor: {doctor_name}
🏥 Service: {service}

Please arrive 10 minutes before your scheduled time.

To confirm or reschedule, call us at {clinic_phone}.

See you soon!

Best regards,
{clinic_name}
{clinic_address}
"""
    
    else:  # low risk
        subject = f"See You Tomorrow - {date_str}"
        message = f"""Dear {patient_name},

Looking forward to seeing you!

📅 Date: {date_str}
⏰ Time: {time_str}
👨‍⚕️ Doctor: {doctor_name}

💡 Tips for your visit:
• Bring your ID and any previous reports
• Arrive 10 minutes early
• Stay hydrated

Any questions? Call us at {clinic_phone}.

Warm regards,
{clinic_name}
"""
    
    return {
        'subject': subject,
        'message': message,
        'risk_level': risk_level,
    }