from django.conf import settings


def analytics_settings(request):
    return {
        'CSP_NONCE': getattr(request, 'csp_nonce', ''),
        'PLAUSIBLE_DOMAIN': getattr(settings, 'PLAUSIBLE_DOMAIN', ''),
        'PLAUSIBLE_SCRIPT_URL': getattr(settings, 'PLAUSIBLE_SCRIPT_URL', ''),
    }
