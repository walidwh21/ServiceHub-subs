from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Offering(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="offerings")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.PositiveIntegerField(default=12)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category__name", "name"]

    def __str__(self):
        return self.name


class ServiceRequest(models.Model):
    PENDING, APPROVED, REJECTED = "pending", "approved", "rejected"
    STATUS_CHOICES = [(PENDING, "Pending"), (APPROVED, "Approved"), (REJECTED, "Rejected")]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requests")
    offering = models.ForeignKey(Offering, on_delete=models.CASCADE, related_name="requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.offering} for {self.customer}"


class SupportTicket(models.Model):
    OPEN, ANSWERED = "open", "answered"
    STATUS_CHOICES = [(OPEN, "Open"), (ANSWERED, "Answered")]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    subject = models.CharField(max_length=120)
    message = models.TextField(max_length=1000)
    response = models.TextField(max_length=1000, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject
