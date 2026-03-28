import os
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from feedback.models import Feedback

from .models import DigestSubscription, ReportComment, ReportFollow, Scamreports, Scamtype


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SecurityHardeningTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.csrf_client = Client(enforce_csrf_checks=True)
        self.staff_user = User.objects.create_user(
            username='staff',
            password='pass12345',
            email='staff@example.com',
            is_staff=True,
        )
        self.owner = User.objects.create_user(
            username='owner',
            password='pass12345',
            email='owner@example.com',
        )
        self.scam_type = Scamtype.objects.create(name='Phishing')
        self.report = Scamreports.objects.create(
            user=self.owner,
            name_or_number='Scammer 1',
            social_media='telegram',
            description='Initial report',
            is_hidden=False,
        )
        self.report.scam_type.add(self.scam_type)

    def test_deploy_init_requires_authenticated_staff_and_csrf(self):
        response = self.client.post(reverse('deploy_init'))
        self.assertEqual(response.status_code, 302)

        self.csrf_client.force_login(self.staff_user)
        response = self.csrf_client.post(reverse('deploy_init'))
        self.assertEqual(response.status_code, 403)

    @patch.dict(os.environ, {'CRON_SECRET': 'cron-secret'}, clear=False)
    @patch('Scam_reports.views.send_weekly_digest', return_value={'status': 'sent', 'message': 'ok'})
    @override_settings(CRON_ALLOWED_IPS=['203.0.113.10'])
    def test_cron_weekly_digest_requires_allowed_ip_and_secret(self, send_digest):
        blocked = self.client.get(
            reverse('cron_weekly_digest'),
            HTTP_AUTHORIZATION='Bearer cron-secret',
            REMOTE_ADDR='198.51.100.7',
        )
        self.assertEqual(blocked.status_code, 403)
        send_digest.assert_not_called()

        allowed = self.client.get(
            reverse('cron_weekly_digest'),
            HTTP_AUTHORIZATION='Bearer cron-secret',
            REMOTE_ADDR='203.0.113.10',
        )
        self.assertEqual(allowed.status_code, 200)
        send_digest.assert_called_once()

    def test_digest_subscription_requires_email_confirmation(self):
        response = self.client.post(reverse('digest_subscribe'), {'email': 'USER@Example.com'})
        self.assertEqual(response.status_code, 200)

        subscription = DigestSubscription.objects.get(email='user@example.com')
        self.assertFalse(subscription.is_verified)
        self.assertTrue(subscription.verification_token)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(subscription.verification_token, mail.outbox[0].body)

        confirm_response = self.client.get(
            reverse('verify_digest_subscription', args=[subscription.verification_token])
        )
        self.assertEqual(confirm_response.status_code, 200)

        subscription.refresh_from_db()
        self.assertTrue(subscription.is_verified)
        self.assertEqual(subscription.verification_token, '')

    def test_follow_report_requires_email_confirmation(self):
        response = self.client.post(
            reverse('follow_report', args=[self.report.id]),
            {'email': 'Watcher@Example.com'},
        )
        self.assertEqual(response.status_code, 200)

        follow = ReportFollow.objects.get(report=self.report, email='watcher@example.com')
        self.assertFalse(follow.is_verified)
        self.assertTrue(follow.verification_token)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(follow.verification_token, mail.outbox[0].body)

        confirm_response = self.client.get(reverse('verify_report_follow', args=[follow.verification_token]))
        self.assertEqual(confirm_response.status_code, 200)

        follow.refresh_from_db()
        self.assertTrue(follow.is_verified)
        self.assertEqual(follow.verification_token, '')

    def test_comment_submission_is_rate_limited(self):
        url = reverse('add_comment', args=[self.report.id])
        payload = {'name': 'Anon', 'message': 'Comment'}

        for _ in range(5):
            response = self.client.post(url, payload, REMOTE_ADDR='198.51.100.8')
            self.assertEqual(response.status_code, 200)

        blocked = self.client.post(url, payload, REMOTE_ADDR='198.51.100.8')
        self.assertEqual(blocked.status_code, 302)
        self.assertEqual(ReportComment.objects.filter(report=self.report).count(), 5)

    def test_mark_resolved_sanitizes_reason(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse('mark_resolved', args=[self.report.id]),
            {'resolution_reason': '<script>alert(1)</script> resolved'},
        )
        self.assertEqual(response.status_code, 302)

        self.report.refresh_from_db()
        self.assertTrue(self.report.is_resolved)
        self.assertEqual(self.report.resolution_reason, 'alert(1) resolved')

    def test_report_list_sets_csp_header_and_nonces(self):
        response = self.client.get(reverse('report_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Content-Security-Policy', response.headers)
        self.assertIn('nonce-', response.headers['Content-Security-Policy'])
        self.assertContains(response, 'nonce="')

    def test_password_reset_page_uses_custom_template(self):
        response = self.client.get(reverse('account_reset_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/password_reset.html')
        self.assertContains(response, 'Send reset link')


class DemoDataCommandTests(TestCase):
    def test_seed_demo_data_is_repeatable(self):
        call_command('seed_demo_data', verbosity=0)
        call_command('seed_demo_data', verbosity=0)

        self.assertTrue(User.objects.filter(username='demo_admin', is_staff=True).exists())
        self.assertTrue(User.objects.filter(username='miriam').exists())
        self.assertGreaterEqual(Scamreports.objects.count(), 8)
        self.assertGreaterEqual(ReportComment.objects.count(), 5)
        self.assertGreaterEqual(ReportFollow.objects.count(), 5)
        self.assertGreaterEqual(DigestSubscription.objects.count(), 3)
        self.assertGreaterEqual(Feedback.objects.count(), 2)
