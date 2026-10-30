from unittest.mock import Mock

import pytest

from app.billing import (BkashAdapter, ChildFee, PaymentError, SeniorFee,
                         StandardFee, fee_strategy_for)
from app.services import ConflictError


@pytest.mark.parametrize("age, strategy, fee", [
    (30, StandardFee, 800), (65, SeniorFee, 560), (8, ChildFee, 400)])
def test_fee_strategy_selected_by_age(age, strategy, fee):
    s = fee_strategy_for(age)
    assert isinstance(s, strategy) and s.compute(800) == fee


def test_adapter_converts_taka_to_poisha():
    client = Mock()
    client.create_payment.return_value = {"status": "SUCCESS", "trx_id": "TRX1"}
    assert BkashAdapter(client).charge(560.5, "INV-1") == "TRX1"
    client.create_payment.assert_called_once_with(amount_poisha=56050, invoice="INV-1")


def test_adapter_raises_on_declined_payment():
    client = Mock()
    client.create_payment.return_value = {"status": "FAILED", "message": "Insufficient balance"}
    with pytest.raises(PaymentError, match="Insufficient"):
        BkashAdapter(client).charge(100, "INV-2")


def test_pay_invoice_uses_gateway_once(svc, gateway, booked):
    gateway.charge.return_value = "TRX42"
    inv = svc.pay(booked["invoice"]["id"])
    assert inv["paid"] == 1 and inv["txn_id"] == "TRX42"
    gateway.charge.assert_called_once_with(800, reference=f"INV-{inv['id']}")
    with pytest.raises(ConflictError):
        svc.pay(inv["id"])
