from django.conf import settings

def base_url(request):
    """
    Add BASE_URL to template context
    """
    return {
        'BASE_URL': settings.BASE_URL
    }