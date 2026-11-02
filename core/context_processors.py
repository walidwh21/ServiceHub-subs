from django.conf import settings

from .brands import BRANDS, get_brand


def brand(request):
    slug = request.session.get("brand") if settings.DEBUG else None
    current = get_brand(slug or settings.BRAND)
    return {
        "brand": current,
        "t": current.terms,
        "currency": settings.CURRENCY_SYMBOL,
        "all_brands": list(BRANDS.values()) if settings.DEBUG else [],
    }
