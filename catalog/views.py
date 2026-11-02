from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import CategoryForm, OfferingForm, TicketForm, TicketResponseForm
from .models import Category, Offering, ServiceRequest, SupportTicket

User = get_user_model()


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only staff users may use these views. Anonymous users go to login, others get 403."""

    def test_func(self):
        return self.request.user.is_staff


# --------------------------------------------------------------------- dashboard
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if request.user.is_staff:
        counts = {s: ServiceRequest.objects.filter(status=s).count() for s, _ in ServiceRequest.STATUS_CHOICES}
        ctx = {
            "customers": User.objects.filter(is_staff=False).count(),
            "offerings": Offering.objects.count(),
            "categories": Category.objects.count(),
            "open_tickets": SupportTicket.objects.filter(status=SupportTicket.OPEN).count(),
            "total_requests": sum(counts.values()),
            "counts": counts,
            "recent": ServiceRequest.objects.select_related("customer", "offering")[:5],
        }
        return render(request, "catalog/dashboard_staff.html", ctx)
    mine = ServiceRequest.objects.filter(customer=request.user)
    ctx = {
        "available": Offering.objects.filter(is_active=True).count(),
        "my_requests": mine.count(),
        "my_approved": mine.filter(status=ServiceRequest.APPROVED).count(),
        "my_tickets": SupportTicket.objects.filter(customer=request.user).count(),
        "recent": mine.select_related("offering")[:5],
    }
    return render(request, "catalog/dashboard_customer.html", ctx)


# ----------------------------------------------------------------- staff: catalog
class CategoryList(StaffRequiredMixin, ListView):
    model = Category
    template_name = "catalog/category_list.html"

    def get_queryset(self):
        return Category.objects.annotate(offering_count=Count("offerings"))


class CategoryCreate(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:category-list")
    success_message = "Category saved."
    extra_context = {"title": "New category"}


class CategoryUpdate(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:category-list")
    success_message = "Category updated."
    extra_context = {"title": "Edit category"}


class CategoryDelete(StaffRequiredMixin, DeleteView):
    model = Category
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:category-list")


class OfferingList(StaffRequiredMixin, ListView):
    model = Offering
    template_name = "catalog/offering_list.html"

    def get_queryset(self):
        return Offering.objects.select_related("category")


class OfferingCreate(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Offering
    form_class = OfferingForm
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:offering-list")
    success_message = "Saved."
    extra_context = {"title": "New item"}


class OfferingUpdate(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Offering
    form_class = OfferingForm
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:offering-list")
    success_message = "Updated."
    extra_context = {"title": "Edit item"}


class OfferingDelete(StaffRequiredMixin, DeleteView):
    model = Offering
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:offering-list")


# --------------------------------------------------------- staff: requests, people
class RequestList(StaffRequiredMixin, ListView):
    model = ServiceRequest
    template_name = "catalog/request_list.html"

    def get_queryset(self):
        qs = ServiceRequest.objects.select_related("customer", "offering")
        status = self.request.GET.get("status")
        if status in dict(ServiceRequest.STATUS_CHOICES):
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["current_status"] = self.request.GET.get("status", "")
        return ctx


@require_POST
def decide_request(request, pk, decision):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect("accounts:login")
    status = {"approve": ServiceRequest.APPROVED, "reject": ServiceRequest.REJECTED}.get(decision)
    if status is None:
        return redirect("catalog:request-list")
    obj = get_object_or_404(ServiceRequest, pk=pk)
    obj.status = status
    obj.save(update_fields=["status", "updated_at"])
    messages.success(request, f"Marked as {obj.get_status_display().lower()}.")
    return redirect("catalog:request-list")


class CustomerList(StaffRequiredMixin, ListView):
    template_name = "catalog/customer_list.html"
    context_object_name = "customers"

    def get_queryset(self):
        return (
            User.objects.filter(is_staff=False)
            .select_related("profile")
            .annotate(request_count=Count("requests"))
            .order_by("first_name", "username")
        )


class CustomerDelete(StaffRequiredMixin, DeleteView):
    model = User
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:customer-list")

    def get_queryset(self):
        return User.objects.filter(is_staff=False)


class TicketList(StaffRequiredMixin, ListView):
    model = SupportTicket
    template_name = "catalog/ticket_list_staff.html"

    def get_queryset(self):
        return SupportTicket.objects.select_related("customer")


class TicketRespond(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SupportTicket
    form_class = TicketResponseForm
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:ticket-list")
    success_message = "Response saved."
    extra_context = {"title": "Respond to ticket"}


# ------------------------------------------------------------------- customer side
class Browse(LoginRequiredMixin, ListView):
    template_name = "catalog/browse.html"
    context_object_name = "offerings"

    def get_queryset(self):
        qs = Offering.objects.filter(is_active=True).select_related("category")
        category = self.request.GET.get("category")
        if category and category.isdigit():
            qs = qs.filter(category_id=int(category))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["current_category"] = self.request.GET.get("category", "")
        return ctx


@require_POST
def create_request(request, pk):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    offering = get_object_or_404(Offering, pk=pk, is_active=True)
    _, created = ServiceRequest.objects.get_or_create(
        customer=request.user,
        offering=offering,
        status=ServiceRequest.PENDING,
    )
    if created:
        messages.success(request, f"Request sent for {offering.name}.")
    else:
        messages.info(request, f"You already have a pending request for {offering.name}.")
    return redirect("catalog:my-requests")


class MyRequests(LoginRequiredMixin, ListView):
    template_name = "catalog/my_requests.html"
    context_object_name = "requests_list"

    def get_queryset(self):
        return ServiceRequest.objects.filter(customer=self.request.user).select_related("offering")


class MyTickets(LoginRequiredMixin, ListView):
    template_name = "catalog/my_tickets.html"
    context_object_name = "tickets"

    def get_queryset(self):
        return SupportTicket.objects.filter(customer=self.request.user)


class TicketCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = SupportTicket
    form_class = TicketForm
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:my-tickets")
    success_message = "Your question was sent."
    extra_context = {"title": "Ask a question"}

    def form_valid(self, form):
        form.instance.customer = self.request.user
        return super().form_valid(form)
