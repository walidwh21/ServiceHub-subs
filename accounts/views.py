from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignUpForm


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("catalog:dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Welcome! Your account is ready.")
        return response
