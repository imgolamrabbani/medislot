"""API + OpenAPI contract tests (the Swagger spec is part of the product)."""
import pytest
from fastapi.testclient import TestClient

from app.main import TAGS, create_app
from tests.conftest import SLOT


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(str(tmp_path / "test.db")))


def test_full_booking_flow_over_http(client):
    pid = client.post("/patients", json={"name": "Rahim", "phone": "01712345678", "age": 70}).json()["id"]
    did = client.post("/doctors", json={"name": "Dr. N", "specialty": "Eye", "fee": 1000}).json()["id"]
    appt = client.post("/appointments", json={"patient_id": pid, "doctor_id": did, "slot": SLOT})
    assert appt.status_code == 201 and appt.json()["invoice"]["amount"] == 700

    again = client.post("/appointments", json={"patient_id": pid, "doctor_id": did, "slot": SLOT})
    assert again.status_code == 409

    paid = client.post(f"/invoices/{appt.json()['invoice']['id']}/pay").json()
    assert paid["paid"] == 1 and paid["txn_id"].startswith("TRX")
    assert client.post(f"/appointments/{appt.json()['id']}/cancel").json()["status"] == "CANCELLED"
    assert len(client.get("/notifications").json()) == 2
    for path in ("/patients", "/doctors", "/appointments", "/invoices"):
        assert len(client.get(path).json()) == 1
    assert client.get("/").status_code == 200


def test_errors_are_mapped_to_http_codes(client):
    assert client.post("/patients", json={"name": "X", "phone": "1", "age": 5}).status_code == 400
    assert client.post("/invoices/99/pay").status_code == 404


def test_openapi_contract_documents_every_module(client):
    spec = client.get("/openapi.json").json()
    assert spec["info"]["title"] == "MediSlot API"
    used_tags = {t for p in spec["paths"].values() for op in p.values() for t in op["tags"]}
    assert used_tags == {t["name"] for t in TAGS}
    assert "409" in spec["paths"]["/appointments"]["post"]["responses"]
    assert client.get("/docs").status_code == 200
