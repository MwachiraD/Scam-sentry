
from django import forms
import os
from .models import (
    Scamreports,
    Scamtype,
    ReportAbuse,
    ReportFollow,
    ReportComment,
    WatchlistItem,
    DigestSubscription,
)

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


class ReportFollowForm(forms.ModelForm):
    class Meta:
        model = ReportFollow
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'})
        }


class ReportCommentForm(forms.ModelForm):
    class Meta:
        model = ReportComment
        fields = ['name', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name (optional)'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a public comment...'}),
        }


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



