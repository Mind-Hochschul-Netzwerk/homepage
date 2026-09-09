from datetime import datetime
from django.test import TestCase
from .models import Event


class EventModelTests(TestCase):
    def test_descriptive_date_single_day(self):
        event = Event(
            title="Single Day Event",
            description="A single day event.",
            date=datetime.fromisoformat("2023-09-02 10:00:00"),
            end_date=None,
            location="Location A",
        )
        self.assertEqual(event.descriptive_date(), "2. September 2023")

    def test_descriptive_date_same_day(self):
        event = Event(
            title="Same Day Event",
            description="Start and end on the same day.",
            date=datetime.fromisoformat("2023-09-02 10:00:00"),
            end_date=datetime.fromisoformat("2023-09-02 18:00:00"),
            location="Location A",
        )
        self.assertEqual(event.descriptive_date(), "2. September 2023")

    def test_descriptive_date_same_month(self):
        event = Event(
            title="Same Month Event",
            description="An event spanning the same month.",
            date=datetime.fromisoformat("2023-09-02 10:00:00"),
            end_date=datetime.fromisoformat("2023-09-05 18:00:00"),
            location="Location B",
        )
        self.assertEqual(event.descriptive_date(), "2. bis 5. September 2023")

    def test_descriptive_date_different_months(self):
        event = Event(
            title="Different Months Event",
            description="An event spanning different months.",
            date=datetime.fromisoformat("2023-08-30 10:00:00"),
            end_date=datetime.fromisoformat("2023-09-05 18:00:00"),
            location="Location C",
        )
        self.assertEqual(
            event.descriptive_date(), "30. August bis 5. September 2023"
        )

    def test_descriptive_date_different_years(self):
        event = Event(
            title="Different Years Event",
            description="An event spanning different years.",
            date=datetime.fromisoformat("2023-12-30 10:00:00"),
            end_date=datetime.fromisoformat("2024-01-05 18:00:00"),
            location="Location D",
        )
        self.assertEqual(
            event.descriptive_date(), "30. Dezember 2023 bis 5. Januar 2024"
        )
