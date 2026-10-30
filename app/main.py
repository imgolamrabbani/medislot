"""REST API documented with OpenAPI/Swagger (served at /docs)."""
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from .billing import BkashAdapter, PaymentError, SandboxBkashClient
from .db import connect
from .events import EventBus
from .notifications import NotifierFactory, subscribe_notifications
from .services import ClinicService, ConflictError, NotFoundError

TAGS = [
    {"name": "Patients", "description": "Register and list patients"},
    {"name": "Doctors", "description": "Manage doctors and consultation fees"},
    {"name": "Appointments", "description": "Book and cancel time slots"},
    {"name": "Billing", "description": "Invoices and payments via bKash adapter"},
    {"name": "Notifications", "description": "Messages sent to patients"},
]


class PatientIn(BaseModel):
    name: str = Field(examples=["Rahim Uddin"])
    phone: str = Field(examples=["01712345678"])
    age: int = Field(examples=[34])


class DoctorIn(BaseModel):
    name: str = Field(examples=["Dr. Nasrin Akter"])
    specialty: str = Field(examples=["Cardiology"])
    fee: float = Field(examples=[800])


class AppointmentIn(BaseModel):
    patient_id: int = Field(examples=[1])
    doctor_id: int = Field(examples=[1])
    slot: str = Field(examples=["2026-11-05T10:30"], description="ISO date-time")


def create_app(db_path="medislot.db", gateway=None, notifier=None) -> FastAPI:
    app = FastAPI(title="MediSlot API", version="1.0.0", openapi_tags=TAGS,
                  description="Clinic appointment and billing system (CSE 3206 Lab 6).")
    bus = EventBus()
    notifier = notifier or NotifierFactory.create("inapp")
    subscribe_notifications(bus, notifier)
    svc = ClinicService(connect(db_path), gateway or BkashAdapter(SandboxBkashClient()), bus)

    errors = {NotFoundError: 404, ValueError: 400, ConflictError: 409, PaymentError: 402}
    for exc, code in errors.items():
        app.add_exception_handler(exc, lambda r, e, c=code: JSONResponse(
            status_code=c, content={"detail": str(e)}))

    @app.get("/", include_in_schema=False)
    def ui():
        return FileResponse(Path(__file__).parent / "static" / "index.html")

    @app.post("/patients", tags=["Patients"], status_code=201)
    def register_patient(p: PatientIn):
        return svc.register_patient(p.name, p.phone, p.age)

    @app.get("/patients", tags=["Patients"])
    def list_patients():
        return svc.patients.find()

    @app.post("/doctors", tags=["Doctors"], status_code=201)
    def add_doctor(d: DoctorIn):
        return svc.add_doctor(d.name, d.specialty, d.fee)

    @app.get("/doctors", tags=["Doctors"])
    def list_doctors():
        return svc.doctors.find()

    @app.post("/appointments", tags=["Appointments"], status_code=201,
              responses={409: {"description": "Slot already booked"}})
    def book(a: AppointmentIn):
        return svc.book(a.patient_id, a.doctor_id, a.slot)

    @app.get("/appointments", tags=["Appointments"])
    def list_appointments():
        return svc.appointments.find()

    @app.post("/appointments/{appointment_id}/cancel", tags=["Appointments"])
    def cancel(appointment_id: int):
        return svc.cancel(appointment_id)

    @app.get("/invoices", tags=["Billing"])
    def list_invoices():
        return svc.invoices.find()

    @app.post("/invoices/{invoice_id}/pay", tags=["Billing"],
              responses={402: {"description": "Payment declined"}})
    def pay(invoice_id: int):
        return svc.pay(invoice_id)

    @app.get("/notifications", tags=["Notifications"])
    def notifications():
        return getattr(notifier, "outbox", [])

    return app


app = create_app()
