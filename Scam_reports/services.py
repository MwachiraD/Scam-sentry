import secrets
from datetime import timedelta

from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from .models import DigestSubscription, ReportFollow, Scamreports


def _generate_verification_token():
    return secrets.token_urlsafe(32)


def _send_confirmation_email(subject, message, recipient):
    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[recipient],
        fail_silently=False,
    )


def create_or_refresh_report_follow(report, email, request):
    follow, created = ReportFollow.objects.get_or_create(report=report, email=email)
    if not created and follow.is_verified:
        return follow, False

    follow.is_verified = False
    follow.verification_token = _generate_verification_token()
    follow.verified_at = None
    follow.save(update_fields=['is_verified', 'verification_token', 'verified_at'])

    confirmation_url = request.build_absolute_uri(
        reverse('verify_report_follow', args=[follow.verification_token])
    )
    _send_confirmation_email(
        subject='Confirm your Scam Sentry report alert',
        message=(
            f'Confirm your alert subscription for "{report.name_or_number}" by opening this link:\n\n'
            f'{confirmation_url}\n\n'
            'If you did not request this alert, you can ignore this email.'
        ),
        recipient=follow.email,
    )
    return follow, True


def verify_report_follow_token(token):
    follow = ReportFollow.objects.filter(verification_token=token).select_related('report').first()
    if not follow:
        return None

    if not follow.is_verified:
        follow.is_verified = True
        follow.verification_token = ''
        follow.verified_at = timezone.now()
        follow.save(update_fields=['is_verified', 'verification_token', 'verified_at'])
    return follow


def create_or_refresh_digest_subscription(email, request, user=None):
    subscription, created = DigestSubscription.objects.get_or_create(email=email)
    changed_fields = []
    if user and subscription.user_id != user.id:
        subscription.user = user
        changed_fields.append('user')

    if not created and subscription.is_verified and subscription.is_active:
        if changed_fields:
            subscription.save(update_fields=changed_fields)
        return subscription, False

    subscription.is_active = True
    subscription.is_verified = False
    subscription.verification_token = _generate_verification_token()
    subscription.verified_at = None
    changed_fields.extend(['is_active', 'is_verified', 'verification_token', 'verified_at'])
    subscription.save(update_fields=changed_fields)

    confirmation_url = request.build_absolute_uri(
        reverse('verify_digest_subscription', args=[subscription.verification_token])
    )
    _send_confirmation_email(
        subject='Confirm your Scam Sentry weekly digest subscription',
        message=(
            'Confirm your weekly Scam Sentry digest subscription by opening this link:\n\n'
            f'{confirmation_url}\n\n'
            'If you did not request this subscription, you can ignore this email.'
        ),
        recipient=subscription.email,
    )
    return subscription, True


def verify_digest_subscription_token(token):
    subscription = DigestSubscription.objects.filter(verification_token=token).first()
    if not subscription:
        return None

    if not subscription.is_verified:
        subscription.is_verified = True
        subscription.verification_token = ''
        subscription.verified_at = timezone.now()
        subscription.save(update_fields=['is_verified', 'verification_token', 'verified_at'])
    return subscription


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
        DigestSubscription.objects.filter(is_active=True, is_verified=True).values_list('email', flat=True)
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
