from django.db import models
from django.contrib.auth.models import User

class Scamtype(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

class Scamreports(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE , null=True , blank=True)
    is_resolved=models.BooleanField(default=False)
    resolution_reason=models.CharField(max_length=120, blank=True)
    is_hidden=models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)
    encounter_count=models.PositiveIntegerField(default=0)
    evidence_text=models.TextField(blank=True, null=True)
    evidence_file=models.FileField(upload_to='evidence_files/', blank=True, null=True)
    date_reported=models.DateTimeField(auto_now_add=True)
    name_or_number=models.CharField(max_length=100, help_text="Name or phone number of the Scammer")
    social_media=models.CharField(max_length=100, help_text="Social media handle e.g  Discord, Telegram. Twitter(x),  etc")
    description=models.TextField()
    scam_type=models.ManyToManyField(Scamtype, related_name="reports")

    def __str__(self):
        return f"{self.scam_type} - {self.name_or_number} - {self.social_media}"

    @property
    def confidence_label(self):
        if self.is_verified:
            return "Verified"
        if self.encounter_count >= 5:
            return "Multiple reports"
        if self.encounter_count >= 1:
            return "Some reports"
        return "New/Unverified"

    @property
    def confidence_class(self):
        if self.is_verified:
            return "bg-success"
        if self.encounter_count >= 5:
            return "bg-warning text-dark"
        if self.encounter_count >= 1:
            return "bg-info text-dark"
        return "bg-secondary"

    @property
    def safety_tips(self):
        tips = set()
        scam_names = [s.name.lower() for s in self.scam_type.all()]
        if any("phishing" in n for n in scam_names):
            tips.add("Never click links from unknown senders.")
            tips.add("Verify the sender through an official channel.")
        if any("impersonation" in n for n in scam_names):
            tips.add("Ask for a callback using an official number.")
        if any("crypto" in n for n in scam_names):
            tips.add("Be cautious with urgent requests to send crypto.")
        if any("romance" in n for n in scam_names):
            tips.add("Never send money to someone you haven't met.")
        if any("tech support" in n for n in scam_names):
            tips.add("No real company asks for remote access unexpectedly.")
        if any("investment" in n for n in scam_names):
            tips.add("Promises of guaranteed returns are a red flag.")
        if any("charity" in n for n in scam_names):
            tips.add("Donate through official, verified sites only.")
        if not tips:
            tips.add("Verify identities and avoid urgent payment requests.")
        return sorted(tips)

    @property
    def pattern_summary(self):
        scam_names = [s.name.lower() for s in self.scam_type.all()]
        if any("phishing" in n for n in scam_names):
            return "Common tactic: fake links and urgent account warnings."
        if any("impersonation" in n for n in scam_names):
            return "Common tactic: pretending to be a trusted person or brand."
        if any("investment" in n for n in scam_names):
            return "Common tactic: high returns with low risk claims."
        if any("romance" in n for n in scam_names):
            return "Common tactic: emotional manipulation and money requests."
        if any("crypto" in n for n in scam_names):
            return "Common tactic: urgent transfer requests or fake exchanges."
        if any("tech support" in n for n in scam_names):
            return "Common tactic: fake alerts requesting remote access."
        return "Common tactic: urgency, secrecy, or unusual payment methods."


class ReportFollow(models.Model):
    report = models.ForeignKey(Scamreports, on_delete=models.CASCADE, related_name="follows")
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} -> {self.report_id}"


class ReportComment(models.Model):
    report = models.ForeignKey(Scamreports, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=80, blank=True)
    message = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment {self.id} on {self.report_id}"


class ReportAbuse(models.Model):
    REASONS = [
        ("personal_info", "Contains personal information"),
        ("false_report", "False or misleading report"),
        ("harassment", "Harassment or hate speech"),
        ("other", "Other"),
    ]
    STATUSES = [
        ("open", "Open"),
        ("reviewing", "Reviewing"),
        ("resolved", "Resolved"),
    ]

    report = models.ForeignKey(Scamreports, on_delete=models.CASCADE, related_name="abuse_reports")
    reason = models.CharField(max_length=50, choices=REASONS)
    email = models.EmailField(blank=True)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Abuse report #{self.id} for {self.report_id}"
    

