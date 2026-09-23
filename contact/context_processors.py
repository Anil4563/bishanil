from .models import ContactSettings

def contact_settings(request):
    try:
        settings = ContactSettings.objects.first()
    except:
        settings = None
    return {'contact_settings': settings}