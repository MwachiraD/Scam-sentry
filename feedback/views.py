import logging
from ipaddress import ip_address

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import render
from django.core.mail import send_mail

from .forms import FeedbackForm

logger = logging.getLogger(__name__)


def _normalized_ip(value):
    try:
        return str(ip_address((value or '').strip()))
    except ValueError:
        return ''


def _get_client_ip(request):
    remote_addr = _normalized_ip(request.META.get('REMOTE_ADDR', ''))
    if getattr(settings, 'TRUST_X_FORWARDED_FOR', False):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded:
            forwarded_ip = _normalized_ip(forwarded.split(',')[0])
            if forwarded_ip:
                return forwarded_ip
    return remote_addr


def _rate_limited(request, key, limit, window_seconds):
    ip = _get_client_ip(request)
    if not ip:
        return False
    cache_key = f"feedback-rl:{key}:{ip}"
    current = cache.get(cache_key)
    if current is None:
        cache.set(cache_key, 1, window_seconds)
        return False
    if current >= limit:
        logger.warning('feedback rate limit triggered key=%s ip=%s path=%s', key, ip, request.path)
        return True
    cache.incr(cache_key)
    return False


# Create your views here.
def feedback_view(request):
    if request.method == 'POST':
        if _rate_limited(request, 'submit', limit=5, window_seconds=3600):
            messages.error(request, 'Too many feedback submissions from this address. Please try again later.')
            return render(request, 'feedback/feedback_form.html', {'form': FeedbackForm()}, status=429)
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save()

            # Send email
            send_mail(
                subject="📬 New Feedback on Scam Sentry",
                message=f"Name: {feedback.name or 'Anonymous'}\nEmail: {feedback.email or 'N/A'}\n\nMessage:\n{feedback.message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )

            return render(request, 'feedback/thank_you.html')
    else:
        form = FeedbackForm()
    return render(request, 'feedback/feedback_form.html', {'form': form})
