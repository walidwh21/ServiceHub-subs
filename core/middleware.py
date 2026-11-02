from django.conf import settings

from .brands import BRANDS


class BrandSwitchMiddleware:
    """In DEBUG only, `?brand=tesla` previews another brand for the session."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        slug = request.GET.get("brand")
        if settings.DEBUG and slug in BRANDS:
            request.session["brand"] = slug
        return self.get_response(request)
