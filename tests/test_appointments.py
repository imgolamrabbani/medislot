from unittest.mock import Mock

import pytest

from app.db import Repository
from app.events import EventBus
from app.services import ClinicService, ConflictError, NotFoundError
from tests.conftest import SLOT


def test_booking_creates_appointment_and_invoice(booked):
    assert booked["status"] == "BOOKED"
    assert booked["invoice"]["amount"] == 800


def test_double_booking_same_slot_is_rejected(svc, booked):
    with pytest.raises(ConflictError):
        svc.book(booked["patient_id"], booked["doctor_id"], SLOT)


def test_cancel_frees_the_slot(svc, booked):
    assert svc.cancel(booked["id"])["status"] == "CANCELLED"
    assert svc.book(booked["patient_id"], booked["doctor_id"], SLOT)["status"] == "BOOKED"
    with pytest.raises(ConflictError):
        svc.cancel(booked["id"])


def test_booking_rejects_past_slot_and_unknown_ids(svc, booked):
    with pytest.raises(ValueError):
        svc.book(booked["patient_id"], booked["doctor_id"], "2000-01-01T10:00")
    with pytest.raises(NotFoundError):
        svc.book(99, booked["doctor_id"], SLOT)


def test_booking_publishes_event(svc):
    listener = Mock()
    svc.bus.subscribe("appointment_booked", listener)
    p = svc.register_patient("Karim", "01811111111", 40)
    d = svc.add_doctor("Dr. Hasan", "Skin", 600)
    svc.book(p["id"], d["id"], SLOT)
    listener.assert_called_once_with(
        {"phone": "01811111111", "doctor": "Dr. Hasan", "slot": SLOT, "amount": 600})


def test_book_with_mocked_repositories():
    """Database fully mocked: service logic is tested in isolation."""
    repos = {t: Mock(spec=Repository, table=t)
             for t in ("patients", "doctors", "appointments", "invoices")}
    repos["patients"].get.return_value = {"id": 1, "age": 65, "phone": "01700000000"}
    repos["doctors"].get.return_value = {"id": 2, "name": "Dr. X", "fee": 1000}
    repos["appointments"].find.return_value = []
    repos["appointments"].add.return_value = {"id": 7}
    svc = ClinicService(None, Mock(), EventBus(), repos=repos)

    svc.book(1, 2, SLOT)

    repos["invoices"].add.assert_called_once_with(appointment_id=7, amount=700.0)
