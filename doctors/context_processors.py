def doctor_profile(request):
    if request.user.is_authenticated:
        try:
            from .models import Doctor
            doctor = Doctor.objects.get(user=request.user)
            return {'doctor_profile': doctor}
        except:
            pass
    return {'doctor_profile': None}