from unittest.mock import Mock

import pytest

from app.events import EventBus
from app.notifications import (InAppNotifier, NotifierFactory, SMSNotifier,
                               subscribe_notifications)


def test_factory_creates_notifier_by_channel():
    assert isinstance(NotifierFactory.create("inapp"), InAppNotifier)
    assert isinstance(NotifierFactory.create("sms", client=Mock()), SMSNotifier)
    with pytest.raises(ValueError):
        NotifierFactory.create("pigeon")
    NotifierFactory.register("email", InAppNotifier)   # new channel, factory unchanged
    assert isinstance(NotifierFactory.create("email"), InAppNotifier)


def test_sms_notifier_calls_external_api():
    client = Mock()                               # network is mocked
    SMSNotifier(client).send("01712345678", "Hi")
    client.post.assert_called_once_with("/sms/send", json={"to": "01712345678", "text": "Hi"})


def test_notifications_follow_appointment_events():
    bus, notifier = EventBus(), InAppNotifier()
    subscribe_notifications(bus, notifier)
    bus.publish("appointment_booked",
                {"phone": "017", "doctor": "Dr. A", "slot": "S1", "amount": 500})
    bus.publish("appointment_cancelled", {"phone": "017", "slot": "S1"})
    assert [m["message"] for m in notifier.outbox] == [
        "Confirmed with Dr. A at S1. Fee: 500 BDT",
        "Your appointment at S1 was cancelled."]
