from datetime import timedelta
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from Scam_reports.models import Scamreports, DigestSubscription


class Command(BaseCommand):
    help = "Send a weekly digest of trending scams to subscribers."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=7)
        reports = Scamreports.objects.filter(is_hidden=False, date_reported__gte=cutoff).order_by('-encounter_count')[:10]
        if not reports:
            self.stdout.write("No reports found for digest.")
            return

        lines = ["Weekly Scam Digest", ""]
        for report in reports:
            lines.append(f"- {report.name_or_number} ({report.social_media})")
        body = "\n".join(lines)

        recipients = list(DigestSubscription.objects.filter(is_active=True).values_list('email', flat=True))
        if not recipients:
            self.stdout.write("No active subscribers.")
            return

        send_mail(
            subject="Scam Sentry Weekly Digest",
            message=body,
            from_email=None,
            recipient_list=recipients,
            fail_silently=False,
        )

        self.stdout.write(f"Sent digest to {len(recipients)} subscribers.")
