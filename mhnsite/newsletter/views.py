from django.http import Http404
from django.shortcuts import render
from django.core import signing
from django.utils import timezone

from .forms import NewsletterSubscriptionForm
from .models import NewsletterSnippet


def subscribe(request):
    snippet = NewsletterSnippet.objects.first()
    if snippet is None:
        raise Http404("No newsletter snippet has been configured.")

    initial = {}
    if request.method == "GET":
        initial["started_at"] = signing.dumps(timezone.now().isoformat())

    form = NewsletterSubscriptionForm(request.POST or None, initial=initial)
    submitted = False

    if (
        request.method == "POST"
        and request.POST.get("status", "") == ""
        and form.is_valid()
    ):
        try:
            started_at = timezone.datetime.fromisoformat(
                signing.loads(form.cleaned_data["started_at"])
            )
        except (signing.BadSignature, TypeError, ValueError):
            started_at = None

        if (
            started_at is not None
            and (timezone.now() - started_at).total_seconds() >= 3
        ):
            submitted = snippet.submit_to_listmonk(
                email=form.cleaned_data["email"],
                name=form.cleaned_data["name"],
            )
            if not submitted:
                form.add_error(
                    None,
                    "Die Anmeldung konnte gerade nicht abgeschlossen werden. "
                    "Bitte versuche es später erneut.",
                )

    return render(
        request,
        "newsletter/subscribe.html",
        {"newsletter": snippet, "form": form, "submitted": submitted},
    )
