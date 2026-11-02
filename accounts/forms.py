from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Profile

User = get_user_model()


class SignUpForm(UserCreationForm):
    phone = forms.CharField(max_length=30, required=False)
    location = forms.CharField(max_length=80, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.update_or_create(
                user=user,
                defaults={"phone": self.cleaned_data["phone"], "location": self.cleaned_data["location"]},
            )
        return user
