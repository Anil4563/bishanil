from django.shortcuts import render, get_object_or_404
from .models import DentalService, DentalFAQ

def service_list(request):
    """Display all dental services"""
    services = DentalService.objects.filter(is_active=True)
    
    # Group by service type
    grouped_services = {}
    for service in services:
        grouped_services[service.service_type] = grouped_services.get(service.service_type, [])
        grouped_services[service.service_type].append(service)
    
    context = {
        'services': services,
        'grouped_services': grouped_services,
        'service_types': DentalService.SERVICE_TYPES,
    }
    return render(request, 'dental/service_list.html', context)

def service_detail(request, slug):
    """Display detailed information about a specific dental service"""
    service = get_object_or_404(DentalService, slug=slug, is_active=True)
    procedures = service.procedures.all()
    faqs = service.faqs.filter(is_active=True)
    
    # Get related services (same type, exclude current)
    related_services = DentalService.objects.filter(
        service_type=service.service_type, 
        is_active=True
    ).exclude(id=service.id)[:3]
    
    context = {
        'service': service,
        'procedures': procedures,
        'faqs': faqs,
        'related_services': related_services,
    }
    return render(request, 'dental/service_detail.html', context)