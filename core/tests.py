from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Offering, ServiceRequest

User = get_user_model()


class AccessAndFlowTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user("boss", password="pw-12345-x", is_staff=True)
        self.cust = User.objects.create_user("cust", password="pw-12345-x")
        cat = Category.objects.create(name="Cat")
        self.item = Offering.objects.create(category=cat, name="Item", price=10)

    def test_customer_cannot_open_staff_pages(self):
        self.client.login(username="cust", password="pw-12345-x")
        self.assertEqual(self.client.get(reverse("catalog:category-list")).status_code, 403)
        self.assertEqual(self.client.get(reverse("catalog:request-list")).status_code, 403)

    def test_anonymous_is_sent_to_login(self):
        resp = self.client.get(reverse("catalog:browse"))
        self.assertEqual(resp.status_code, 302)

    def test_request_then_approve(self):
        self.client.login(username="cust", password="pw-12345-x")
        self.client.post(reverse("catalog:create-request", args=[self.item.pk]))
        req = ServiceRequest.objects.get()
        self.assertEqual(req.status, ServiceRequest.PENDING)
        self.client.post(reverse("catalog:create-request", args=[self.item.pk]))
        self.assertEqual(ServiceRequest.objects.count(), 1)  # no duplicates

        self.client.logout()
        self.client.login(username="boss", password="pw-12345-x")
        self.client.post(reverse("catalog:request-decide", args=[req.pk, "approve"]))
        req.refresh_from_db()
        self.assertEqual(req.status, ServiceRequest.APPROVED)

    def test_decide_requires_post(self):
        self.client.login(username="boss", password="pw-12345-x")
        resp = self.client.get(reverse("catalog:request-decide", args=[1, "approve"]))
        self.assertEqual(resp.status_code, 405)

    def test_signup_creates_customer(self):
        resp = self.client.post(reverse("accounts:signup"), {
            "first_name": "A", "last_name": "B", "username": "newbie", "email": "",
            "password1": "S0me-long-pass!", "password2": "S0me-long-pass!",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(User.objects.get(username="newbie").is_staff)
