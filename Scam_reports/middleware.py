import base64
import os

from .utils import ensure_google_social_app

_social_app_checked = False


class GoogleSocialAppMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _social_app_checked

        if not _social_app_checked:
            _social_app_checked = ensure_google_social_app()

        return self.get_response(request)


class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = base64.b64encode(os.urandom(16)).decode('ascii')
        response = self.get_response(request)
        response['Content-Security-Policy'] = self._build_policy(request.csp_nonce)
        return response

    def _build_policy(self, nonce):
        policy = {
            'default-src': ["'self'"],
            'base-uri': ["'self'"],
            'connect-src': ["'self'", 'https://plausible.io'],
            'font-src': ["'self'", 'data:', 'https://cdnjs.cloudflare.com', 'https://fonts.gstatic.com'],
            'form-action': ["'self'"],
            'frame-ancestors': ["'none'"],
            'img-src': ["'self'", 'blob:', 'data:', 'https:'],
            'object-src': ["'none'"],
            'script-src': [
                "'self'",
                f"'nonce-{nonce}'",
                'https://cdn.jsdelivr.net',
                'https://plausible.io',
            ],
            'style-src': [
                "'self'",
                "'unsafe-inline'",
                'https://cdn.jsdelivr.net',
                'https://cdnjs.cloudflare.com',
                'https://fonts.googleapis.com',
            ],
        }
        return '; '.join(f"{directive} {' '.join(values)}" for directive, values in policy.items())
