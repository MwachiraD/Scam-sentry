from django.db import models
from django.contrib.auth.models import User

class Scamtype(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

class Scamreports(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE , null=True , blank=True)
    is_resolved=models.BooleanField(default=False)
    evidence_text=models.TextField(blank=True, null=True)
    evidence_file=models.FileField(upload_to='evidence_files/', blank=True, null=True)
    date_reported=models.DateTimeField(auto_now_add=True)
    name_or_number=models.CharField(max_length=100, help_text="Name or phone number of the Scammer")
    social_media=models.CharField(max_length=100, help_text="Social media handle e.g  Discord, Telegram. Twitter(x),  etc")
    description=models.TextField()
    scam_type=models.ManyToManyField(Scamtype, related_name="reports")

    def __str__(self):
        return f"{self.scam_type} - {self.name_or_number} - {self.social_media}"
    

