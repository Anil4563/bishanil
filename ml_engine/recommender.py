"""
Doctor Recommendation Module
Ranks doctors by quality score and finds similar doctors.
"""

from django.db.models import Avg, Count


def calculate_doctor_score(doctor):
    """
    Calculate a quality score for a doctor.
    
    Formula:
        score = (avg_rating × 0.5) + (experience × 0.3) + (appointments × 0.2)
    
    Returns:
        {
            'score': float,
            'rating_component': float,
            'experience_component': float,
            'appointment_component': float,
            'avg_rating': float,
            'total_appointments': int,
        }
    """
    # Get average rating from feedbacks
    feedbacks = doctor.feedbacks.filter(is_approved=True)
    if feedbacks.exists():
        avg_rating = feedbacks.aggregate(avg=Avg('rating'))['avg'] or 0
    else:
        avg_rating = 0
    
    # Get total appointments
    from appointments.models import Appointment
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    
    # Normalize values (0-1 scale for weighted scoring)
    normalized_rating = avg_rating / 5.0  # 0 to 1
    normalized_experience = min(doctor.experience_years / 20.0, 1.0)  # Cap at 20 years
    normalized_appointments = min(total_appointments / 50.0, 1.0)  # Cap at 50 appointments
    
    # Apply weights
    rating_component = normalized_rating * 0.5
    experience_component = normalized_experience * 0.3
    appointment_component = normalized_appointments * 0.2
    
    final_score = rating_component + experience_component + appointment_component
    
    return {
        'score': round(final_score, 4),
        'rating_component': round(rating_component, 4),
        'experience_component': round(experience_component, 4),
        'appointment_component': round(appointment_component, 4),
        'avg_rating': round(avg_rating, 2),
        'total_appointments': total_appointments,
    }


def get_recommended_doctors(limit=3):
    """
    Get top-rated doctors based on score.
    
    Returns: List of dicts with doctor + score info
    """
    from doctors.models import Doctor
    
    doctors = Doctor.objects.filter(is_active=True, is_approved=True)
    scored = []
    
    for doctor in doctors:
        score_data = calculate_doctor_score(doctor)
        scored.append({
            'doctor': doctor,
            'score': score_data['score'],
            'avg_rating': score_data['avg_rating'],
            'total_appointments': score_data['total_appointments'],
        })
    
    # Sort by score (highest first)
    scored.sort(key=lambda x: x['score'], reverse=True)
    
    return scored[:limit]


def get_similar_doctors(doctor, limit=3):
    """
    Find doctors similar to the given doctor.
    
    Similarity based on:
    - Same specialization type (high weight)
    - Close experience level
    - Close fee range
    """
    from doctors.models import Doctor
    
    all_doctors = Doctor.objects.filter(
        is_active=True, 
        is_approved=True
    ).exclude(id=doctor.id)
    
    similarities = []
    
    for other in all_doctors:
        # Similarity score
        similarity = 0
        
        # 1. Same specialization type (40 points)
        if other.specialization_type == doctor.specialization_type:
            similarity += 40
        
        # 2. Experience closeness (30 points)
        exp_diff = abs(other.experience_years - doctor.experience_years)
        exp_similarity = max(0, 30 - (exp_diff * 3))
        similarity += exp_similarity
        
        # 3. Fee closeness (20 points)
        fee_diff = abs(float(other.consultation_fee) - float(doctor.consultation_fee))
        fee_similarity = max(0, 20 - (fee_diff / 100))
        similarity += fee_similarity
        
        # 4. Degree match (10 points)
        if other.degree == doctor.degree:
            similarity += 10
        
        similarities.append({
            'doctor': other,
            'similarity': round(similarity, 2),
        })
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    return similarities[:limit]


def get_all_doctor_rankings():
    """
    Get all doctors with their ranking scores.
    Used for the admin panel.
    """
    from doctors.models import Doctor
    
    doctors = Doctor.objects.filter(is_active=True, is_approved=True)
    scored = []
    
    for doctor in doctors:
        score_data = calculate_doctor_score(doctor)
        scored.append({
            'doctor': doctor,
            'score': score_data['score'],
            'avg_rating': score_data['avg_rating'],
            'total_appointments': score_data['total_appointments'],
            'rating_component': score_data['rating_component'],
            'experience_component': score_data['experience_component'],
            'appointment_component': score_data['appointment_component'],
        })
    
    # Sort by score
    scored.sort(key=lambda x: x['score'], reverse=True)
    
    # Add rank
    for i, item in enumerate(scored, 1):
        item['rank'] = i
    
    return scored