from django.core.management.base import BaseCommand

from Scam_reports.models import Scamtype


DEFAULT_TYPES = [
    'Phishing',
    'Impersonation',
    'Investment Scam',
    'Fake Job',
    'Romance Scam',
    'Giveaway Scam',
    'Crypto Scam',
    'Tech Support Scam',
    'Charity Scam',
]


class Command(BaseCommand):
    help = "Seed default scam types."

    def handle(self, *args, **options):
        created_count = 0
        for name in DEFAULT_TYPES:
            _, created = Scamtype.objects.get_or_create(name=name)
            if created:
                created_count += 1
        self.stdout.write(
            self.style.SUCCESS(f"Seeded scam types. Added: {created_count}.")
        )
