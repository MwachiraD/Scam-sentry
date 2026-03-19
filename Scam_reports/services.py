from datetime import timedelta

from django.core.mail import send_mail
from django.utils import timezone

from .models import DigestSubscription, Scamreports


def send_weekly_digest():
    cutoff = timezone.now() - timedelta(days=7)
    reports = Scamreports.objects.filter(
        is_hidden=False,
        date_reported__gte=cutoff,
    ).order_by('-encounter_count')[:10]
    if not reports:
        return {
            'status': 'noop',
            'message': 'No reports found for digest.',
            'recipient_count': 0,
            'report_count': 0,
        }

    recipients = list(
        DigestSubscription.objects.filter(is_active=True).values_list('email', flat=True)
    )
    if not recipients:
        return {
            'status': 'noop',
            'message': 'No active subscribers.',
            'recipient_count': 0,
            'report_count': len(reports),
        }

    lines = ['Weekly Scam Digest', '']
    for report in reports:
        lines.append(f'- {report.name_or_number} ({report.social_media})')

    send_mail(
        subject='Scam Sentry Weekly Digest',
        message='\n'.join(lines),
        from_email=None,
        recipient_list=recipients,
        fail_silently=False,
    )

    return {
        'status': 'sent',
        'message': f'Sent digest to {len(recipients)} subscribers.',
        'recipient_count': len(recipients),
        'report_count': len(reports),
    }
