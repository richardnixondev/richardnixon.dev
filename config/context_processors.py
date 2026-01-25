from django.conf import settings


def umami(request):
    """Add Umami Analytics website ID to template context."""
    return {
        'UMAMI_WEBSITE_ID': getattr(settings, 'UMAMI_WEBSITE_ID', ''),
    }
