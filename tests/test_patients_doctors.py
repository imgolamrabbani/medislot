import pytest


def test_register_patient_is_persisted(svc):
    p = svc.register_patient("Rahim", "01712345678", 30)
    assert svc.patients.get(p["id"])["name"] == "Rahim"


@pytest.mark.parametrize("name, phone, age", [
    ("", "01712345678", 30),          # empty name
    ("Rahim", "12345", 30),           # bad phone
    ("Rahim", "01712345678", 150),    # bad age
])
def test_register_patient_rejects_invalid_input(svc, name, phone, age):
    with pytest.raises(ValueError):
        svc.register_patient(name, phone, age)


def test_add_doctor_requires_positive_fee(svc):
    assert svc.add_doctor("Dr. Kamal", "ENT", 500)["fee"] == 500
    with pytest.raises(ValueError):
        svc.add_doctor("Dr. Kamal", "ENT", 0)
