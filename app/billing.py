"""Billing module: Strategy (fee rules) + Adapter (third-party payment SDK)."""
import uuid
from abc import ABC, abstractmethod


# ---------- Strategy ----------
class FeeStrategy(ABC):
    @abstractmethod
    def compute(self, base_fee: float) -> float: ...


class StandardFee(FeeStrategy):
    def compute(self, base_fee):
        return round(base_fee, 2)


class SeniorFee(FeeStrategy):          # age >= 60 -> 30% off
    def compute(self, base_fee):
        return round(base_fee * 0.70, 2)


class ChildFee(FeeStrategy):           # age < 12 -> 50% off
    def compute(self, base_fee):
        return round(base_fee * 0.50, 2)


def fee_strategy_for(age: int) -> FeeStrategy:
    if age >= 60:
        return SeniorFee()
    if age < 12:
        return ChildFee()
    return StandardFee()


# ---------- Adapter ----------
class PaymentError(Exception):
    pass


class PaymentGateway(ABC):
    """Target interface the application depends on."""

    @abstractmethod
    def charge(self, amount: float, reference: str) -> str: ...


class BkashAdapter(PaymentGateway):
    """Adapts a bKash-style SDK (amount in poisha, dict response) to PaymentGateway."""

    def __init__(self, client):
        self.client = client

    def charge(self, amount, reference):
        resp = self.client.create_payment(amount_poisha=round(amount * 100), invoice=reference)
        if resp.get("status") != "SUCCESS":
            raise PaymentError(resp.get("message", "Payment declined"))
        return resp["trx_id"]


class SandboxBkashClient:
    """Offline stand-in for the real SDK, used for local demo runs."""

    def create_payment(self, amount_poisha: int, invoice: str) -> dict:
        return {"status": "SUCCESS", "trx_id": "TRX" + uuid.uuid4().hex[:8].upper()}
