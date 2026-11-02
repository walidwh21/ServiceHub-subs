from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from catalog.models import Offering

from .brands import get_brand
from .forms import ContactForm


def home(request):
    featured = list(Offering.objects.filter(is_active=True).select_related("category")[:3])
    if not featured:  # empty database: show the brand's sample catalogue
        for cat_name, _desc, items in get_brand(settings.BRAND).seed:
            for name, desc, price, months in items:
                featured.append({"name": name, "description": desc, "price": price,
                                 "duration_months": months, "category": {"name": cat_name}})
        featured = featured[:3]
    return render(request, "core/home.html", {"featured": featured})


def about(request):
    return render(request, "core/about.html")


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        send_mail(
            subject=f"[{get_brand(settings.BRAND).name}] Message from {data['name']}",
            message=f"From: {data['name']} <{data['email']}>\n\n{data['message']}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_RECIPIENT],
        )
        messages.success(request, "Thanks - your message was sent.")
        return redirect("core:contact")
    return render(request, "core/contact.html", {"form": form})
