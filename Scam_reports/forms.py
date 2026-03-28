
from django import forms
import os
from django.utils.html import strip_tags
from .models import (
    Scamreports,
    Scamtype,
    ReportAbuse,
    ReportFollow,
    ReportComment,
    WatchlistItem,
    DigestSubscription,
)


def _clean_plain_text(value):
    if value in (None, ''):
        return value
    return strip_tags(str(value)).replace('\x00', '').strip()


class Scamreportform(forms.ModelForm):
    scam_type = forms.ModelMultipleChoiceField(
        queryset=Scamtype.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=True,  # or False, if optional
        label="Scam Types"
    )

    class Meta:
        model = Scamreports
        fields = [
            'name_or_number',
            'social_media',
            'description',
            'evidence_text',
            'evidence_file',
            'scam_type',
        ]

    def clean_name_or_number(self):
        return _clean_plain_text(self.cleaned_data['name_or_number'])

    def clean_social_media(self):
        return _clean_plain_text(self.cleaned_data['social_media'])

    def clean_description(self):
        return _clean_plain_text(self.cleaned_data['description'])

    def clean_evidence_text(self):
        return _clean_plain_text(self.cleaned_data.get('evidence_text'))

    def clean_evidence_file(self):
        evidence_file = self.cleaned_data.get('evidence_file')
        if not evidence_file:
            return evidence_file

        max_size_mb = 5
        if evidence_file.size > max_size_mb * 1024 * 1024:
            raise forms.ValidationError(f"Evidence file must be under {max_size_mb}MB.")

        allowed_types = {
            'application/pdf',
            'image/jpeg',
            'image/png',
            'image/webp',
        }
        content_type = getattr(evidence_file, 'content_type', '')
        if content_type and content_type not in allowed_types:
            raise forms.ValidationError("Unsupported file type. Use PDF, JPG, PNG, or WebP.")

        ext = os.path.splitext(evidence_file.name)[1].lower()
        if ext not in {'.pdf', '.jpg', '.jpeg', '.png', '.webp'}:
            raise forms.ValidationError("Unsupported file extension. Use PDF, JPG, PNG, or WebP.")

        return evidence_file


class ReportAbuseForm(forms.ModelForm):
    class Meta:
        model = ReportAbuse
        fields = ['reason', 'email', 'details']
        widgets = {
            'details': forms.Textarea(attrs={'rows': 4})
        }

    def clean_email(self):
        return self.cleaned_data.get('email', '').strip().lower()

    def clean_details(self):
        return _clean_plain_text(self.cleaned_data.get('details'))


class ReportFollowForm(forms.ModelForm):
    class Meta:
        model = ReportFollow
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'})
        }

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()


class ReportCommentForm(forms.ModelForm):
    class Meta:
        model = ReportComment
        fields = ['name', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name (optional)'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a public comment...'}),
        }

    def clean_name(self):
        return _clean_plain_text(self.cleaned_data.get('name'))

    def clean_message(self):
        return _clean_plain_text(self.cleaned_data['message'])


class WatchlistForm(forms.ModelForm):
    class Meta:
        model = WatchlistItem
        fields = []


class DigestSubscriptionForm(forms.ModelForm):
    class Meta:
        model = DigestSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'})
        }

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()


class ResolutionForm(forms.Form):
    resolution_reason = forms.CharField(required=False, max_length=120)

    def clean_resolution_reason(self):
        return _clean_plain_text(self.cleaned_data.get('resolution_reason', ''))



