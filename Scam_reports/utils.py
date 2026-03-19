import os
from urllib.parse import urlparse

from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import OperationalError, ProgrammingError


def _site_domain():
    site_url = getattr(settings, 'SITE_URL', '').strip()
    if site_url:
        parsed = urlparse(site_url if '://' in site_url else f'https://{site_url}')
        return parsed.netloc or parsed.path

    for env_name in ('VERCEL_PROJECT_PRODUCTION_URL', 'VERCEL_URL', 'RENDER_EXTERNAL_HOSTNAME'):
        value = os.environ.get(env_name, '').strip()
        if value:
            return value

    return 'localhost:8000'


def ensure_google_social_app():
    try:
        site, _ = Site.objects.update_or_create(
            id=1,
            defaults={'domain': _site_domain(), 'name': settings.SITE_NAME},
        )
        app, _ = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': settings.GOOGLE_CLIENT_ID,
                'secret': settings.GOOGLE_CLIENT_SECRET,
            },
        )
        app.sites.add(site)
        return True
    except (OperationalError, ProgrammingError):
        return False
