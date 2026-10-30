import pytest

from app.billing import ChildFee, SeniorFee, StandardFee, fee_strategy_for


@pytest.mark.parametrize("age, strategy, fee", [
    (30, StandardFee, 800), (65, SeniorFee, 560), (8, ChildFee, 400)])
def test_fee_strategy_selected_by_age(age, strategy, fee):
    s = fee_strategy_for(age)
    assert isinstance(s, strategy) and s.compute(800) == fee
