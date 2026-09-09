from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PublishingPanel
from wagtail.fields import RichTextField
from wagtail.models import DraftStateMixin, PreviewableMixin, RevisionMixin
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.snippets.models import register_snippet


@register_snippet
class FooterText(
    DraftStateMixin, RevisionMixin, PreviewableMixin, models.Model
):
    body = RichTextField()

    panels = [FieldPanel("body"), PublishingPanel()]

    def __str__(self):
        return "Footer text"

    def get_preview_template(self, request, mode_name):
        return "base.html"

    def get_preview_context(self, request, mode_name):
        return {"footer_text": self.body}

    class Meta:
        verbose_name_plural = "Footer Text"
