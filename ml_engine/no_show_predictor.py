"""
Patient No-Show Prediction Module
Uses Logistic Regression to predict if a patient will skip their appointment.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime


def extract_appointment_features(appointment):
    """
    Convert an Appointment into a feature vector for ML.
    
    Features:
    [0] Patient age (normalized)
    [1] Day of week (0-6, normalized)
    [2] Is appointment in the morning? (0/1)
    [3] Lead time in days (normalized, capped at 30)
    [4] Patient's past no-show count (normalized)
    [5] Service type: dental (0) or eye (1)
    [6] Has symptoms? (0/1)
    [7] Booking hour of day (normalized)
    """
    from appointments.models import Appointment
    
    features = []
    
    # 1. Age
    age = appointment.patient_age or 30
    features.append(min(age / 100.0, 1.0))
    
    # 2. Day of week
    dow = appointment.appointment_date.weekday()  # 0=Monday, 6=Sunday
    features.append(dow / 6.0)
    
    # 3. Morning? (before noon)
    is_morning = 1.0 if appointment.appointment_time.hour < 12 else 0.0
    features.append(is_morning)
    
    # 4. Lead time (days between booking and appointment)
    try:
        booked_date = appointment.created_at.date()
        lead_days = (appointment.appointment_date - booked_date).days
        lead_days = max(0, min(lead_days, 30))
        features.append(lead_days / 30.0)
    except:
        features.append(0.5)
    
    # 5. Past no-shows by this patient
    past = Appointment.objects.filter(
        patient_email=appointment.patient_email,
        attendance_status='not_came'
    ).exclude(id=appointment.id).count()
    features.append(min(past / 5.0, 1.0))
    
    # 6. Service type
    features.append(0.0 if appointment.service_type == 'dental' else 1.0)
    
    # 7. Has symptoms?
    has_symptoms = 1.0 if appointment.symptoms and appointment.symptoms.strip() else 0.0
    features.append(has_symptoms)
    
    # 8. Booking hour
    try:
        hour = appointment.created_at.hour
        features.append(hour / 24.0)
    except:
        features.append(0.5)
    
    return features


def get_training_data():
    """
    Get all completed/past appointments with known attendance status.
    
    Returns: (X, y) where:
        X = feature matrix
        y = labels (0=came, 1=not_came)
    """
    from appointments.models import Appointment
    
    # Only use appointments where we know the attendance
    appointments = Appointment.objects.filter(
        attendance_status__in=['came', 'not_came']
    )
    
    X = []
    y = []
    
    for apt in appointments:
        try:
            features = extract_appointment_features(apt)
            X.append(features)
            y.append(1 if apt.attendance_status == 'not_came' else 0)
        except:
            continue
    
    return np.array(X), np.array(y)


def train_model():
    """
    Train the Logistic Regression model.
    
    Returns: (model, scaler) or (None, None) if insufficient data
    """
    X, y = get_training_data()
    
    if len(X) < 10:
        return None, None, {
            'error': 'Not enough training data',
            'samples': len(X),
            'needed': 10
        }
    
    # Check if we have both classes
    unique_classes = np.unique(y)
    if len(unique_classes) < 2:
        return None, None, {
            'error': 'Need both "came" and "not_came" samples',
            'came': int(np.sum(y == 0)),
            'not_came': int(np.sum(y == 1))
        }
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Logistic Regression
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_scaled, y)
    
    # Calculate training accuracy
    accuracy = model.score(X_scaled, y)
    
    return model, scaler, {
        'success': True,
        'samples': len(X),
        'accuracy': round(accuracy * 100, 1),
        'came': int(np.sum(y == 0)),
        'not_came': int(np.sum(y == 1)),
    }


def predict_no_show(appointment):
    """
    Predict no-show probability for a given appointment.
    
    Returns:
    {
        'probability': float (0-100),
        'risk_level': 'low' | 'medium' | 'high',
        'risk_color': 'success' | 'warning' | 'danger',
        'message': str,
        'model_ready': bool,
    }
    """
    model, scaler, info = train_model()
    
    if model is None:
        return {
            'probability': 50.0,
            'risk_level': 'unknown',
            'risk_color': 'warning',
            'message': 'Model needs more training data',
            'model_ready': False,
        }
    
    try:
        features = np.array([extract_appointment_features(appointment)])
        features_scaled = scaler.transform(features)
        
        # Get probability of class 1 (no-show)
        prob = model.predict_proba(features_scaled)[0][1] * 100
        prob = round(prob, 1)
        
        # Classify risk level
        if prob < 25:
            risk = 'low'
            color = 'success'
            message = 'Low risk — likely to attend'
        elif prob < 50:
            risk = 'medium'
            color = 'warning'
            message = 'Medium risk — consider a reminder'
        else:
            risk = 'high'
            color = 'danger'
            message = 'High risk — send extra reminder'
        
        return {
            'probability': prob,
            'risk_level': risk,
            'risk_color': color,
            'message': message,
            'model_ready': True,
        }
    except Exception as e:
        return {
            'probability': 50.0,
            'risk_level': 'unknown',
            'risk_color': 'warning',
            'message': f'Error: {str(e)}',
            'model_ready': False,
        }


def get_model_info():
    """Get info about the trained model (for admin panel)."""
    model, scaler, info = train_model()
    return info