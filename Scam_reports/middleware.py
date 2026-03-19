from .utils import ensure_google_social_app

_social_app_checked = False


class GoogleSocialAppMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _social_app_checked

        if not _social_app_checked:
            ensure_google_social_app()
            _social_app_checked = True

        return self.get_response(request)
