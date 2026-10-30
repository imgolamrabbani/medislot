import pytest

from app.billing import calculate_fee


@pytest.mark.parametrize("age, fee", [(30, 800), (65, 560), (8, 400)])
def test_fee_depends_on_age(age, fee):
    assert calculate_fee(age, 800) == fee
