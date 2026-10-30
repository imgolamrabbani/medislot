"""Billing module: consultation fee calculation."""


def calculate_fee(age: int, base_fee: float) -> float:
    if age >= 60:
        return round(base_fee * 0.70, 2)
    elif age < 12:
        return round(base_fee * 0.50, 2)
    else:
        return round(base_fee, 2)
