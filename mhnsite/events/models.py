from django.db import models
from django.utils.formats import date_format
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.fields import RichTextField


class Event(Page):
    description = models.TextField()
    date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        FieldPanel("date"),
        FieldPanel("end_date"),
        FieldPanel("location"),
    ]

    parent_page_types = ["events.EventIndex"]

    def __str__(self):
        return self.title

    def descriptive_date(self):
        """
        Returns a descriptive string for the event's date and time.
        If the event has an end date, it will return a range.
        """

        def _format_date(value):
            return date_format(value, "j. F Y")

        def _format_day_month(value):
            return date_format(value, "j. F")

        if self.end_date:
            if self.date.date().year == self.end_date.date().year:
                if self.date.date().month == self.end_date.date().month:
                    if self.date.date().day == self.end_date.date().day:
                        # Format: 2. September 2023
                        return _format_date(self.date)
                    # Format: 2. bis 5. September 2023
                    return f"{self.date.day}. bis {_format_date(self.end_date)}"
                # Format: 30. August bis 5. September 2023
                return f"{_format_day_month(self.date)} bis {_format_date(self.end_date)}"
            # Format: 30. Dezember 2023 bis 5. Januar 2024
            return (
                f"{_format_date(self.date)} bis {_format_date(self.end_date)}"
            )
        # Format: 2. September 2023
        return _format_date(self.date)


class EventIndex(Page):
    """A page that lists all events."""

    blurb = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("blurb"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context["events"] = Event.objects.live().order_by("date")
        return context
