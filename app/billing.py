"""Billing module: Strategy (fee rules)."""
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
