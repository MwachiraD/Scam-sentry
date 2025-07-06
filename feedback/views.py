from django.shortcuts import render
from .forms import FeedbackForm
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.
def feedback_view(request):
    if request.method == 'POST':
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