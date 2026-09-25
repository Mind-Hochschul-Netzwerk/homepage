from django import forms


class NewsletterSubscriptionForm(forms.Form):
    email = forms.EmailField(label="E-Mail-Adresse")
    name = forms.CharField(label="Name", max_length=255)
    status = forms.CharField(required=False, widget=forms.HiddenInput)
    started_at = forms.CharField(widget=forms.HiddenInput)
