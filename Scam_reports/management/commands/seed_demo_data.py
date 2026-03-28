from datetime import timedelta

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from feedback.models import Feedback

from Scam_reports.management.commands.seed_scam_types import DEFAULT_TYPES
from Scam_reports.models import (
    DigestSubscription,
    ReportAbuse,
    ReportComment,
    ReportEditLog,
    ReportFollow,
    Scamreports,
    Scamtype,
    WatchlistItem,
)


DEMO_USERS = [
    {
        'username': 'demo_admin',
        'email': 'admin@scamsentry.local',
        'first_name': 'Demo',
        'last_name': 'Admin',
        'is_staff': True,
        'is_superuser': True,
        'password': 'DemoAdmin123!',
    },
    {
        'username': 'miriam',
        'email': 'miriam@scamsentry.local',
        'first_name': 'Miriam',
        'last_name': 'Otieno',
        'is_staff': False,
        'is_superuser': False,
        'password': 'ScamSentry123!',
    },
    {
        'username': 'daniel',
        'email': 'daniel@scamsentry.local',
        'first_name': 'Daniel',
        'last_name': 'Mwangi',
        'is_staff': False,
        'is_superuser': False,
        'password': 'ScamSentry123!',
    },
    {
        'username': 'aisha',
        'email': 'aisha@scamsentry.local',
        'first_name': 'Aisha',
        'last_name': 'Hassan',
        'is_staff': False,
        'is_superuser': False,
        'password': 'ScamSentry123!',
    },
]


DEMO_REPORTS = [
    {
        'owner': 'miriam',
        'name_or_number': '0722 555 014',
        'social_media': 'WhatsApp',
        'description': 'Fake recruiter asking for HELB clearance, EACC papers, and a small fast-track payment to secure an interview slot.',
        'evidence_text': 'Caller insisted on M-Pesa payment before interview confirmation.',
        'scam_types': ['Fake Job', 'WhatsApp Scam', 'Impersonation'],
        'reported_days_ago': 1,
        'encounter_count': 19,
        'is_hidden': False,
        'is_verified': True,
        'is_resolved': False,
        'resolution_reason': '',
        'comments': [
            {'name': 'Kevin', 'message': 'Same script used on me last week.', 'is_approved': True},
            {'name': 'Anonymous', 'message': 'They switched to Telegram after I asked for the company office.', 'is_approved': True},
        ],
        'follows': ['alerts+jobs@scamsentry.local'],
    },
    {
        'owner': 'daniel',
        'name_or_number': 'Safaricom-Care KE',
        'social_media': 'Telegram',
        'description': 'Phishing messages claiming your SIM will be blocked unless you verify through a fake portal.',
        'evidence_text': 'Fake support profile used a shortened link with urgent account-warning language.',
        'scam_types': ['Phishing', 'Account Takeover', 'Impersonation'],
        'reported_days_ago': 3,
        'encounter_count': 11,
        'is_hidden': False,
        'is_verified': True,
        'is_resolved': True,
        'resolution_reason': 'Verified as fake and blocked by affected users.',
        'comments': [
            {'name': 'Mary', 'message': 'The link copied the official branding almost exactly.', 'is_approved': True},
        ],
        'follows': ['alerts+telco@scamsentry.local'],
    },
    {
        'owner': 'aisha',
        'name_or_number': 'QuickLoan Desk',
        'social_media': 'Facebook',
        'description': 'Loan page demanding an insurance fee before releasing funds and then going silent.',
        'evidence_text': 'Page requested ID card and upfront fee over Messenger.',
        'scam_types': ['Loan Scam', 'Marketplace Scam'],
        'reported_days_ago': 2,
        'encounter_count': 6,
        'is_hidden': False,
        'is_verified': False,
        'is_resolved': False,
        'resolution_reason': '',
        'comments': [
            {'name': 'James', 'message': 'They kept changing the repayment story after payment.', 'is_approved': True},
            {'name': 'Review queue', 'message': 'Please hide this comment', 'is_approved': False},
        ],
        'follows': ['alerts+loans@scamsentry.local'],
    },
    {
        'owner': None,
        'name_or_number': 'BitLion Academy',
        'social_media': 'Telegram',
        'description': 'Crypto trading group promising guaranteed daily returns and pressuring members to reinvest immediately.',
        'evidence_text': 'Admins removed users who asked for withdrawal proof.',
        'scam_types': ['Crypto Scam', 'Investment Scam'],
        'reported_days_ago': 5,
        'encounter_count': 13,
        'is_hidden': False,
        'is_verified': True,
        'is_resolved': False,
        'resolution_reason': '',
        'comments': [
            {'name': 'Otis', 'message': 'Classic pump-and-dump group behavior.', 'is_approved': True},
        ],
        'follows': ['alerts+crypto@scamsentry.local'],
    },
    {
        'owner': 'daniel',
        'name_or_number': 'County Jobs Board',
        'social_media': 'WhatsApp',
        'description': 'Unverified county-government job flyer requesting payment before interview scheduling.',
        'evidence_text': 'Shared poster used an outdated county logo and personal number.',
        'scam_types': ['Fake Job', 'WhatsApp Scam'],
        'reported_days_ago': 0,
        'encounter_count': 3,
        'is_hidden': True,
        'is_verified': False,
        'is_resolved': False,
        'resolution_reason': '',
        'comments': [],
        'follows': [],
    },
    {
        'owner': 'miriam',
        'name_or_number': 'MamaRose Electronics',
        'social_media': 'Facebook Marketplace',
        'description': 'Seller takes payment for electronics then sends fake courier receipts and disappears.',
        'evidence_text': 'Multiple buyer screenshots show the same bank account reused.',
        'scam_types': ['Marketplace Scam', 'Purchase Scam', 'Delivery Scam'],
        'reported_days_ago': 6,
        'encounter_count': 9,
        'is_hidden': False,
        'is_verified': True,
        'is_resolved': True,
        'resolution_reason': 'Marketplace account reported and removed.',
        'comments': [
            {'name': 'Irene', 'message': 'Lost my deposit after they sent a fake rider receipt.', 'is_approved': True},
        ],
        'follows': ['alerts+market@scamsentry.local'],
        'abuse_reports': [
            {'reason': 'false_report', 'email': 'reviewer@scamsentry.local', 'details': 'Asked team to double-check supplier evidence.', 'status': 'open'},
        ],
    },
    {
        'owner': 'aisha',
        'name_or_number': 'Delivery Hub Express',
        'social_media': 'SMS / WhatsApp',
        'description': 'Fake parcel delivery notice with a tiny fee to reschedule shipment and collect card details.',
        'evidence_text': 'Link pointed to a cloned payment page on a newly registered domain.',
        'scam_types': ['Delivery Scam', 'Phishing'],
        'reported_days_ago': 4,
        'encounter_count': 8,
        'is_hidden': False,
        'is_verified': True,
        'is_resolved': False,
        'resolution_reason': '',
        'comments': [
            {'name': 'Brian', 'message': 'They knew my real area name, so the message felt legitimate.', 'is_approved': True},
        ],
        'follows': [],
    },
    {
        'owner': None,
        'name_or_number': 'Relief Support Kenya',
        'social_media': 'Email',
        'description': 'Charity-themed appeal requesting emergency mobile money transfers after a flood incident.',
        'evidence_text': 'Email domain differed from the real charity by one character.',
        'scam_types': ['Charity Scam', 'Impersonation'],
        'reported_days_ago': 7,
        'encounter_count': 4,
        'is_hidden': False,
        'is_verified': False,
        'is_resolved': False,
        'resolution_reason': '',
        'comments': [
            {'name': 'Faith', 'message': 'They reused old news photos to make the appeal look real.', 'is_approved': True},
        ],
        'follows': ['alerts+charity@scamsentry.local'],
    },
]


class Command(BaseCommand):
    help = 'Seed demo users, reports, comments, follows, watchlists, and subscriptions.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            default='ScamSentry123!',
            help='Password for demo non-admin users.',
        )
        parser.add_argument(
            '--admin-password',
            default='DemoAdmin123!',
            help='Password for the demo admin user.',
        )

    def handle(self, *args, **options):
        password = options['password']
        admin_password = options['admin_password']
        now = timezone.now()

        scam_types = {
            name: Scamtype.objects.get_or_create(name=name)[0]
            for name in DEFAULT_TYPES
        }
        User = get_user_model()
        users = {}

        for fixture in DEMO_USERS:
            user, _ = User.objects.get_or_create(username=fixture['username'])
            user.email = fixture['email']
            user.first_name = fixture['first_name']
            user.last_name = fixture['last_name']
            user.is_staff = fixture['is_staff']
            user.is_superuser = fixture['is_superuser']
            user.is_active = True
            user.set_password(admin_password if fixture['is_superuser'] else password)
            user.save()
            EmailAddress.objects.update_or_create(
                user=user,
                email=user.email,
                defaults={'primary': True, 'verified': True},
            )
            users[fixture['username']] = user

        report_count = 0
        for fixture in DEMO_REPORTS:
            owner = users.get(fixture['owner']) if fixture['owner'] else None
            report, _ = Scamreports.objects.get_or_create(
                user=owner,
                name_or_number=fixture['name_or_number'],
                social_media=fixture['social_media'],
            )
            report.description = fixture['description']
            report.evidence_text = fixture['evidence_text']
            report.encounter_count = fixture['encounter_count']
            report.is_hidden = fixture['is_hidden']
            report.is_verified = fixture['is_verified']
            report.is_resolved = fixture['is_resolved']
            report.resolution_reason = fixture['resolution_reason']
            report.save()

            reported_at = now - timedelta(days=fixture['reported_days_ago'])
            resolved_at = None
            if fixture['is_resolved']:
                resolved_at = reported_at + timedelta(hours=12)
            Scamreports.objects.filter(pk=report.pk).update(
                date_reported=reported_at,
                resolved_at=resolved_at,
            )
            report.refresh_from_db()
            report.scam_type.set([scam_types[name] for name in fixture['scam_types']])
            report_count += 1

            for comment_fixture in fixture.get('comments', []):
                ReportComment.objects.update_or_create(
                    report=report,
                    name=comment_fixture['name'],
                    message=comment_fixture['message'],
                    defaults={'is_approved': comment_fixture['is_approved']},
                )

            for follow_email in fixture.get('follows', []):
                ReportFollow.objects.update_or_create(
                    report=report,
                    email=follow_email,
                    defaults={
                        'is_verified': True,
                        'verification_token': '',
                        'verified_at': now,
                    },
                )

            for abuse_fixture in fixture.get('abuse_reports', []):
                ReportAbuse.objects.update_or_create(
                    report=report,
                    reason=abuse_fixture['reason'],
                    email=abuse_fixture['email'],
                    defaults={
                        'details': abuse_fixture['details'],
                        'status': abuse_fixture['status'],
                    },
                )

            if owner:
                ReportEditLog.objects.get_or_create(
                    report=report,
                    user=owner,
                    changes={'seeded': {'from': None, 'to': 'demo data'}},
                )

        watch_targets = [
            ('miriam', 'BitLion Academy', 'Telegram'),
            ('daniel', '0722 555 014', 'WhatsApp'),
            ('aisha', 'MamaRose Electronics', 'Facebook Marketplace'),
        ]
        for username, name_or_number, social_media in watch_targets:
            WatchlistItem.objects.get_or_create(
                user=users[username],
                name_or_number=name_or_number,
                social_media=social_media,
            )

        for username in ('miriam', 'daniel', 'aisha'):
            user = users[username]
            DigestSubscription.objects.update_or_create(
                email=user.email,
                defaults={
                    'user': user,
                    'is_active': True,
                    'is_verified': True,
                    'verification_token': '',
                    'verified_at': now,
                },
            )

        feedback_items = [
            {
                'name': 'Miriam Otieno',
                'email': 'miriam@scamsentry.local',
                'message': 'The watchlist and moderation views make the app feel much more real.',
            },
            {
                'name': 'Daniel Mwangi',
                'email': 'daniel@scamsentry.local',
                'message': 'Would be good to surface trending scam categories on the homepage.',
            },
        ]
        for feedback_item in feedback_items:
            Feedback.objects.update_or_create(
                email=feedback_item['email'],
                defaults={
                    'name': feedback_item['name'],
                    'message': feedback_item['message'],
                },
            )

        self.stdout.write(self.style.SUCCESS(f'Seeded {report_count} demo reports and {len(users)} demo users.'))
        self.stdout.write('Demo credentials:')
        self.stdout.write(f'  demo_admin / {admin_password}')
        self.stdout.write(f'  miriam / {password}')
        self.stdout.write(f'  daniel / {password}')
        self.stdout.write(f'  aisha / {password}')
