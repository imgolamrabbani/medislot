from unittest.mock import Mock

import pytest

from app.db import connect
from app.events import EventBus
from app.services import ClinicService

SLOT = "2030-01-15T10:00"


@pytest.fixture
def gateway():
    return Mock()


@pytest.fixture
def svc(gateway):
    return ClinicService(connect(":memory:"), gateway, EventBus())
