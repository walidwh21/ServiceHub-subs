from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # staff
    path("categories/", views.CategoryList.as_view(), name="category-list"),
    path("categories/new/", views.CategoryCreate.as_view(), name="category-create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdate.as_view(), name="category-update"),
    path("categories/<int:pk>/delete/", views.CategoryDelete.as_view(), name="category-delete"),
    path("items/", views.OfferingList.as_view(), name="offering-list"),
    path("items/new/", views.OfferingCreate.as_view(), name="offering-create"),
    path("items/<int:pk>/edit/", views.OfferingUpdate.as_view(), name="offering-update"),
    path("items/<int:pk>/delete/", views.OfferingDelete.as_view(), name="offering-delete"),
    path("requests/", views.RequestList.as_view(), name="request-list"),
    path("requests/<int:pk>/<str:decision>/", views.decide_request, name="request-decide"),
    path("customers/", views.CustomerList.as_view(), name="customer-list"),
    path("customers/<int:pk>/delete/", views.CustomerDelete.as_view(), name="customer-delete"),
    path("tickets/", views.TicketList.as_view(), name="ticket-list"),
    path("tickets/<int:pk>/respond/", views.TicketRespond.as_view(), name="ticket-respond"),
    # customer
    path("browse/", views.Browse.as_view(), name="browse"),
    path("browse/<int:pk>/request/", views.create_request, name="create-request"),
    path("my-requests/", views.MyRequests.as_view(), name="my-requests"),
    path("my-tickets/", views.MyTickets.as_view(), name="my-tickets"),
    path("my-tickets/new/", views.TicketCreate.as_view(), name="ticket-create"),
]
