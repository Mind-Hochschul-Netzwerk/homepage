import requests
from django.db import models
from django.conf import settings
from wagtail.snippets.models import register_snippet


@register_snippet
class NewsletterSnippet(models.Model):
    """Form to subscribe to the newsletter."""

    title = models.CharField(max_length=255)
    content = models.TextField()
    # This should present a form to submit an email address and name to Listmonk.

    @classmethod
    def submit_to_listmonk(cls, email: str, name: str) -> bool:
        """Submit the email and name to Listmonk.
        Returns True if the submission was successful, False otherwise.

        Uses settings.LISTMONK_LIST_ID, settings.LISTMONK_URL, settings.LISTMONK_API_USER, and settings.LISTMONK_API_TOKEN for configuration.
        """
        payload = {
            "email": email,
            "name": name,
            "status": "enabled",
            "lists": [settings.LISTMONK_LIST_ID],
        }

        try:
            response = requests.post(
                settings.LISTMONK_URL,
                json=payload,
                auth=(settings.LISTMONK_API_USER, settings.LISTMONK_API_TOKEN),
                timeout=10,
            )
        except requests.RequestException:
            return False

        return 200 <= response.status_code < 300
