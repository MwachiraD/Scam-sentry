from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.conf import settings
from django.db import OperationalError, ProgrammingError

def ensure_google_social_app():
    try:
        site, _ = Site.objects.get_or_create(
            id=1,
            defaults={"domain": "scam-sentry-ke.onrender.com", "name": "Scam Sentry"}
        )

        if not SocialApp.objects.filter(provider="google").exists():
            app = SocialApp.objects.create(
                provider="google",
                name="Google",
                client_id=settings.GOOGLE_CLIENT_ID,
                secret=settings.GOOGLE_CLIENT_SECRET,
            )
            app.sites.add(site)
    except (OperationalError, ProgrammingError):
        pass
