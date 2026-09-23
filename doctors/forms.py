from django import forms
from .models import Doctor

class DoctorRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    
    class Meta:
        model = Doctor
        fields = [
            'name', 'specialization_type', 'degree', 'specialization',
            'experience_years', 'qualifications', 'expertise', 'languages',
            'consultation_fee', 'availability', 'bio', 'education', 'profile_image'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'qualifications': forms.Textarea(attrs={'rows': 3}),
            'expertise': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data