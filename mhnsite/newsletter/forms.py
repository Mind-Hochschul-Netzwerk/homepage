from django import forms


class NewsletterSubscriptionForm(forms.Form):
    email = forms.EmailField(
        label="E-Mail", widget=forms.TextInput(attrs={"class": "text-input"})
    )
    name = forms.CharField(
        label="Name",
        max_length=255,
        widget=forms.EmailInput(attrs={"class": "text-input"}),
    )
    status = forms.CharField(required=False, widget=forms.HiddenInput)
    started_at = forms.CharField(widget=forms.HiddenInput)
