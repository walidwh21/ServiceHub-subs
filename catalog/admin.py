from django.contrib import admin

from .models import Category, Offering, ServiceRequest, SupportTicket

admin.site.register(Category)
admin.site.register(Offering)
admin.site.register(ServiceRequest)
admin.site.register(SupportTicket)
