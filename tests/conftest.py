from unittest.mock import Mock

import pytest

from app.billing import PaymentGateway
from app.db import connect
from app.events import EventBus
from app.services import ClinicService

SLOT = "2030-01-15T10:00"


@pytest.fixture
def gateway():
    return Mock(spec=PaymentGateway)          # no real payment is ever made


@pytest.fixture
def svc(gateway):
    return ClinicService(connect(":memory:"), gateway, EventBus())


@pytest.fixture
def booked(svc):
    p = svc.register_patient("Rahim", "01712345678", 30)
    d = svc.add_doctor("Dr. Nasrin", "Cardiology", 800)
    return svc.book(p["id"], d["id"], SLOT)
