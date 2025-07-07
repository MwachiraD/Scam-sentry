from django.db import migrations

def create_default_scam_types(apps, schema_editor):
    ScamType = apps.get_model('Scam_reports', 'ScamType')
    default_types = [
        'Phishing',
        'Investment Scam',
        'Romance Scam',
        'Fake Job Offer',
        'Lottery/Prize Scam',
        'WhatsApp Scam',
        'M-Pesa Fraud',
        'Impersonation',
        'Loan Scam',
    ]
    for name in default_types:
        ScamType.objects.get_or_create(name=name)

class Migration(migrations.Migration):

    dependencies = [
        ('Scam_reports', '0001_initial'),  
    ]

    operations = [
        migrations.RunPython(create_default_scam_types),
    ]
