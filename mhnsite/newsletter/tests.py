from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import signing

from .models import NewsletterSnippet


@override_settings(
    DEBUG=False,
    MIDDLEWARE=[],
    LISTMONK_LIST_ID=1,
    LISTMONK_URL="https://listmonk.example/api/subscribers",
    LISTMONK_API_USER="user",
    LISTMONK_API_TOKEN="token",
)
class NewsletterSubscriptionTests(TestCase):
    def setUp(self):
        self.snippet = NewsletterSnippet.objects.create(
            title="Newsletter",
            content="Bleib informiert.",
        )

    def get_started_at(self):
        return signing.dumps(
            (datetime.now(timezone.utc) - timedelta(seconds=5)).isoformat()
        )

    def subscribe_url(self):
        return reverse(
            "newsletter_subscribe",
            kwargs={"snippet_id": self.snippet.pk},
        )

    @patch("newsletter.models.requests.post")
    @patch("newsletter.views.timezone.now")
    def test_submits_valid_subscription_to_listmonk(self, now, post):
        started_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        now.return_value = datetime(2026, 1, 1, 0, 0, 3, tzinfo=timezone.utc)
        post.return_value = Mock(status_code=201)

        form_started_at = signing.dumps(started_at.isoformat())
        response = self.client.post(
            self.subscribe_url(),
            {
                "email": "alex@example.com",
                "name": "Alex",
                "started_at": form_started_at,
            },
        )

        self.assertContains(response, "Danke für deine Anmeldung")
        post.assert_called_once_with(
            "https://listmonk.example/api/subscribers",
            json={
                "email": "alex@example.com",
                "name": "Alex",
                "status": "enabled",
                "lists": [1],
            },
            auth=("user", "token"),
            timeout=10,
        )

    @patch("newsletter.models.requests.post")
    def test_does_not_submit_invalid_email(self, post):
        form_started_at = self.get_started_at()
        response = self.client.post(
            self.subscribe_url(),
            {
                "email": "not-an-email",
                "name": "Alex",
                "started_at": form_started_at,
            },
        )

        self.assertContains(response, "Bitte gültige E-Mail-Adresse eingeben.")
        post.assert_not_called()

    def test_uses_the_newsletter_snippet_in_the_request_url(self):
        selected_snippet = NewsletterSnippet.objects.create(
            title="Ausgewählter Newsletter",
            content="Informationen zum ausgewählten Newsletter.",
        )

        response = self.client.post(
            reverse(
                "newsletter_subscribe",
                kwargs={"snippet_id": selected_snippet.pk},
            ),
            {
                "email": "not-an-email",
                "name": "Alex",
                "started_at": self.get_started_at(),
            },
        )

        self.assertContains(response, "Ausgewählter Newsletter")
        self.assertNotContains(response, "<h2>Newsletter</h2>", html=False)

    @patch("newsletter.models.requests.post")
    def test_drops_subscription_with_nonempty_status(self, post):
        form_started_at = self.get_started_at()
        response = self.client.post(
            self.subscribe_url(),
            {
                "email": "alex@example.com",
                "name": "Alex",
                "status": "spam",
                "started_at": form_started_at,
            },
        )

        self.assertNotContains(response, "Danke für deine Anmeldung")
        post.assert_not_called()

    @patch("newsletter.models.requests.post")
    @patch("newsletter.views.timezone.now")
    def test_drops_subscription_submitted_too_quickly(self, now, post):
        started_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        now.side_effect = [
            started_at,
            datetime(2026, 1, 1, 0, 0, 2, tzinfo=timezone.utc),
        ]

        form_started_at = self.get_started_at()
        response = self.client.post(
            self.subscribe_url(),
            {
                "email": "alex@example.com",
                "name": "Alex",
                "started_at": form_started_at,
            },
        )

        self.assertNotContains(response, "Danke für deine Anmeldung")
        post.assert_not_called()
