
from django import forms
from .models import Scamreports, Scamtype

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
