"""Notification module: Factory creates the right Notifier for a channel."""
from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def send(self, to: str, message: str) -> None: ...


class InAppNotifier(Notifier):
    """Stores messages in an outbox (shown at GET /notifications)."""

    def __init__(self):
        self.outbox: list[dict] = []

    def send(self, to, message):
        self.outbox.append({"to": to, "message": message})


class SMSNotifier(Notifier):
    """Sends through an external SMS HTTP API client (network dependency)."""

    def __init__(self, client):
        self.client = client

    def send(self, to, message):
        self.client.post("/sms/send", json={"to": to, "text": message})


class NotifierFactory:
    _registry = {"inapp": InAppNotifier, "sms": SMSNotifier}

    @classmethod
    def register(cls, channel: str, notifier_cls: type) -> None:
        cls._registry[channel] = notifier_cls

    @classmethod
    def create(cls, channel: str, **kwargs) -> Notifier:
        if channel not in cls._registry:
            raise ValueError(f"Unknown channel: {channel}")
        return cls._registry[channel](**kwargs)


def subscribe_notifications(bus, notifier: Notifier) -> None:
    """Observer wiring: notify the patient whenever an appointment changes."""
    bus.subscribe("appointment_booked", lambda e: notifier.send(
        e["phone"], f"Confirmed with {e['doctor']} at {e['slot']}. Fee: {e['amount']} BDT"))
    bus.subscribe("appointment_cancelled", lambda e: notifier.send(
        e["phone"], f"Your appointment at {e['slot']} was cancelled."))
