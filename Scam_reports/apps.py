from django.apps import AppConfig
from django.apps import AppConfig

class ScamReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Scam_reports'

    def ready(self):
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site
        from django.conf import settings
        import django.db.utils

        try:
            site, _ = Site.objects.get_or_create(id=1, defaults={'domain': 'scam-sentry-ke.onrender.com', 'name': 'Scam Sentry'})
            if not SocialApp.objects.filter(provider='google').exists():
                app = SocialApp.objects.create(
                    provider='google',
                    name='Google',
                    client_id=settings.GOOGLE_CLIENT_ID,
                    secret=settings.GOOGLE_CLIENT_SECRET,
                )
                app.sites.add(site)
        except (django.db.utils.OperationalError, django.db.utils.ProgrammingError):
            # Happens during `migrate` or if DB not ready, safe to ignore
            pass
class ScamReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Scam_reports'
