from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from accounts.models import Profile
from catalog.models import Category, Offering, ServiceRequest, SupportTicket
from core.brands import BRANDS, get_brand


class Command(BaseCommand):
    help = "Load a demo catalogue for a brand preset and create two demo users."

    def add_arguments(self, parser):
        parser.add_argument("--brand", default=settings.BRAND, choices=sorted(BRANDS))
        parser.add_argument("--password", default="", help="Password for demo users (random if omitted).")

    def handle(self, *args, **opts):
        brand = get_brand(opts["brand"])
        User = get_user_model()
        password = opts["password"] or get_random_string(14)

        for cat_name, cat_desc, items in brand.seed:
            category, _ = Category.objects.get_or_create(name=cat_name, defaults={"description": cat_desc})
            for name, desc, price, months in items:
                Offering.objects.get_or_create(
                    category=category,
                    name=name,
                    defaults={"description": desc, "price": Decimal(price), "duration_months": months},
                )

        staff, made = User.objects.get_or_create(username="demo_staff", defaults={"is_staff": True, "is_superuser": True})
        customer, made_c = User.objects.get_or_create(
            username="demo_customer", defaults={"first_name": "Sam", "last_name": "Example", "email": "sam@example.com"}
        )
        Profile.objects.get_or_create(user=customer, defaults={"location": "Example City"})
        if made:
            staff.set_password(password)
            staff.save()
        if made_c:
            customer.set_password(password)
            customer.save()
            first = Offering.objects.first()
            if first:
                ServiceRequest.objects.create(customer=customer, offering=first)
            SupportTicket.objects.create(customer=customer, subject="Question about billing", message="When am I charged?")

        self.stdout.write(self.style.SUCCESS(f"Seeded brand '{brand.slug}'."))
        if made or made_c:
            self.stdout.write(f"Demo logins: demo_staff / demo_customer - password: {password}")
        else:
            self.stdout.write("Demo users already existed; passwords unchanged.")
