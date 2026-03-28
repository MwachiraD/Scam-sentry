
from django import forms
from django.utils.html import strip_tags
from .models import Feedback


def _clean_plain_text(value):
    if value in (None, ''):
        return value
    return strip_tags(str(value)).replace('\x00', '').strip()


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4})
        }

    def clean_name(self):
        return _clean_plain_text(self.cleaned_data.get('name'))

    def clean_email(self):
        return self.cleaned_data.get('email', '').strip().lower()

    def clean_message(self):
        return _clean_plain_text(self.cleaned_data['message'])
