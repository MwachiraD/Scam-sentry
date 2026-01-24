from django.db import migrations

def create_default_scam_types(apps, schema_editor):
    Scamtype = apps.get_model('Scam_reports', 'Scamtype')
    default_types = [
        'Phishing',
        'Impersonation',
        'Investment Scam',
        'Fake Job',
        'Romance Scam',
        'Giveaway Scam',
        'Crypto Scam',
        'Tech Support Scam',
        'Charity Scam',
    ]
    for name in default_types:
        Scamtype.objects.get_or_create(name=name)

class Migration(migrations.Migration):

    dependencies = [
        ('Scam_reports', '0001_initial'),  
    ]

    operations = [
        migrations.RunPython(create_default_scam_types),
    ]
