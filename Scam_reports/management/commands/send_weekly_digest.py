from django.core.management.base import BaseCommand

from Scam_reports.services import send_weekly_digest


class Command(BaseCommand):
    help = 'Send a weekly digest of trending scams to subscribers.'

    def handle(self, *args, **options):
        result = send_weekly_digest()
        self.stdout.write(result['message'])
