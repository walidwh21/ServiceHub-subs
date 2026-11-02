from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=60)
    email = forms.EmailField()
    message = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={"rows": 5}))
