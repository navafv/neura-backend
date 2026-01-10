from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Event, Participant

class EventRegistrationTest(TestCase):
    def setUp(self):
        self.past_event = Event.objects.create(
            title="Past Workshop",
            date=timezone.now() - timedelta(days=1),
            max_participants=2
        )
        self.future_event = Event.objects.create(
            title="Future Hackathon",
            date=timezone.now() + timedelta(days=1),
            max_participants=1
        )

    def test_past_event_registration_fails(self):
        # Logic: Test that registering for a past event is blocked in the serializer
        # (Usually tested via API Client in DRF, but here is a model-level check)
        self.assertFalse(self.past_event.is_registration_open)