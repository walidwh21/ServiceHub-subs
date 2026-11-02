from django import forms

from .models import Category, Offering, SupportTicket


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]


class OfferingForm(forms.ModelForm):
    class Meta:
        model = Offering
        fields = ["category", "name", "description", "price", "duration_months", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class TicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["subject", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}


class TicketResponseForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["response"]
        widgets = {"response": forms.Textarea(attrs={"rows": 5})}

    def save(self, commit=True):
        ticket = super().save(commit=False)
        ticket.status = SupportTicket.ANSWERED if ticket.response.strip() else SupportTicket.OPEN
        if commit:
            ticket.save()
        return ticket
