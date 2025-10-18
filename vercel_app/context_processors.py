from django.conf import settings

def base_url(request):
    """
    Add BASE_URL to template context
    """
    return {
        'BASE_URL': getattr(settings, 'BASE_URL', 'http://localhost:8000')
    }