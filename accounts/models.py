from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Optional extra contact details. Everything here is user-supplied and optional."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return f"Profile of {self.user.get_username()}"
