from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.core import signing
from django.utils import timezone

from .forms import NewsletterSubscriptionForm
from .models import NewsletterSnippet


@require_POST
def subscribe(request, snippet_id):
    snippet = get_object_or_404(NewsletterSnippet, pk=snippet_id)
    form = NewsletterSubscriptionForm(request.POST)
    submitted = False
    if form.is_valid():
        # If status is not empty or time to fill was too short, drop the submission to Listmonk and show a generic error message.
        try:
            started_at = timezone.datetime.fromisoformat(
                signing.loads(form.cleaned_data["started_at"])
            )
        except (signing.BadSignature, TypeError, ValueError):
            started_at = None
        too_fast = (
            started_at is None
            or (timezone.now() - started_at).total_seconds() < 3
        )

        if too_fast or request.POST.get("status", "") != "":
            # replace the form with a generic error message to avoid giving clues to bots
            return render(
                request,
                "newsletter/response.html",
                {
                    "title": "Fehler",
                    "message": "Die Anmeldung konnte nicht verarbeitet werden.",
                    "status": "error",
                },
            )
        if form.is_valid():
            submitted = snippet.submit_to_listmonk(
                email=form.cleaned_data["email"],
                name=form.cleaned_data["name"],
            )
            if submitted:
                return render(
                    request,
                    "newsletter/response.html",
                    {
                        "title": "Danke für deine Anmeldung",
                        "message": "Du hast dich erfolgreich für den Newsletter angemeldet.",
                        "status": "success",
                    },
                )
            else:
                form.add_error(
                    None,
                    "Die Anmeldung konnte gerade nicht abgeschlossen werden. "
                    "Bitte versuche es später erneut.",
                )

    return render(
        request,
        "newsletter/subscription_form.html",
        {"newsletter": snippet, "form": form, "submitted": submitted},
    )
