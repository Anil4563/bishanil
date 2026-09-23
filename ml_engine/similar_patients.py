"""
Similar Patients Finder Module
Uses K-Nearest Neighbors (KNN) to find patients with similar medical histories.
"""

import numpy as np
from sklearn.neighbors import NearestNeighbors
from accounts.models import MedicalHistory


def extract_features(medical_history):
    """
    Convert a MedicalHistory record into a numerical feature vector.
    
    Features:
    [0] Age (normalized)
    [1] Diabetes (0/1)
    [2] Thyroid (0/1)
    [3] Asthma (0/1)
    [4] Heart disease (0/1)
    [5] Blood pressure (systolic normalized)
    [6] Has allergies (0/1)
    [7] Has dental issues (0/1)
    [8] Has eye issues (0/1)
    """
    features = []
    
    # 1. Age (normalize to 0-1, cap at 100)
    try:
        age = medical_history.patient.user.profile.date_of_birth
        if age:
            from datetime import date
            age_years = (date.today() - age).days / 365.25
            features.append(min(age_years / 100.0, 1.0))
        else:
            features.append(0.3)  # Default
    except:
        features.append(0.3)
    
    # 2-5. Boolean conditions
    features.append(1.0 if medical_history.diabetes else 0.0)
    features.append(1.0 if medical_history.thyroid else 0.0)
    features.append(1.0 if medical_history.asthma else 0.0)
    features.append(1.0 if medical_history.heart_disease else 0.0)
    
    # 6. Blood pressure (parse "120/80")
    bp_systolic = 120  # Default
    if medical_history.blood_pressure:
        try:
            bp_systolic = int(medical_history.blood_pressure.split('/')[0])
        except:
            pass
    features.append(min(bp_systolic / 200.0, 1.0))
    
    # 7-9. Text-based features (has content or not)
    features.append(1.0 if medical_history.allergies and medical_history.allergies.lower() not in ['none', 'no', ''] else 0.0)
    features.append(1.0 if medical_history.dental_issues and medical_history.dental_issues.lower() not in ['none', 'no', ''] else 0.0)
    features.append(1.0 if medical_history.eye_issues and medical_history.eye_issues.lower() not in ['none', 'no', ''] else 0.0)
    
    return features


def find_similar_patients(target_patient_profile, k=5):
    """
    Find k patients most similar to the target patient.
    
    Args:
        target_patient_profile: PatientProfile instance
        k: number of similar patients to return
    
    Returns:
        List of dicts with:
        {
            'patient': PatientProfile,
            'medical_history': MedicalHistory,
            'similarity': float (0-100),
        }
    """
    # Get all medical histories
    all_histories = MedicalHistory.objects.select_related('patient__user').exclude(
        patient=target_patient_profile
    )
    
    if all_histories.count() == 0:
        return []
    
    # Get target's history
    try:
        target_history = MedicalHistory.objects.get(patient=target_patient_profile)
    except MedicalHistory.DoesNotExist:
        return []
    
    # Extract features
    target_features = np.array([extract_features(target_history)])
    
    # Extract features for all other patients
    patient_data = []
    feature_matrix = []
    
    for history in all_histories:
        try:
            features = extract_features(history)
            feature_matrix.append(features)
            patient_data.append(history)
        except:
            continue
    
    if len(feature_matrix) == 0:
        return []
    
    feature_matrix = np.array(feature_matrix)
    
    # Fit KNN
    n_neighbors = min(k, len(feature_matrix))
    knn = NearestNeighbors(n_neighbors=n_neighbors, metric='euclidean')
    knn.fit(feature_matrix)
    
    # Find neighbors
    distances, indices = knn.kneighbors(target_features)
    
    # Build results
    results = []
    for distance, idx in zip(distances[0], indices[0]):
        history = patient_data[idx]
        
        # Convert distance to similarity percentage
        # Lower distance = higher similarity
        # Max distance in our feature space ≈ sqrt(9) ≈ 3
        similarity = max(0, 100 - (distance * 33.33))
        
        results.append({
            'patient': history.patient,
            'medical_history': history,
            'similarity': round(similarity, 1),
        })
    
    return results


def get_similarity_reason(target_history, other_history):
    """
    Generate a human-readable explanation of why two patients are similar.
    """
    reasons = []
    
    # Check shared conditions
    if target_history.diabetes and other_history.diabetes:
        reasons.append("Both have Diabetes")
    if target_history.thyroid and other_history.thyroid:
        reasons.append("Both have Thyroid")
    if target_history.asthma and other_history.asthma:
        reasons.append("Both have Asthma")
    if target_history.heart_disease and other_history.heart_disease:
        reasons.append("Both have Heart disease")
    
    # Check similar blood pressure
    if target_history.blood_pressure and other_history.blood_pressure:
        try:
            t_bp = int(target_history.blood_pressure.split('/')[0])
            o_bp = int(other_history.blood_pressure.split('/')[0])
            if abs(t_bp - o_bp) <= 10:
                reasons.append("Similar blood pressure")
        except:
            pass
    
    # Check shared allergies
    if target_history.allergies and other_history.allergies:
        if target_history.allergies.lower() == other_history.allergies.lower():
            reasons.append("Same allergies")
    
    if not reasons:
        reasons.append("Similar overall profile")
    
    return ", ".join(reasons[:3])