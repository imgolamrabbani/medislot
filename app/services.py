"""Business logic for all modules. Dependencies are injected (easy to mock)."""
import re
from datetime import datetime

from .billing import fee_strategy_for
from .db import Repository
from .events import EventBus


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class ClinicService:
    def __init__(self, conn, gateway, bus: EventBus | None = None, repos=None):
        repos = repos or {t: Repository(conn, t)
                          for t in ("patients", "doctors", "appointments", "invoices")}
        self.patients, self.doctors = repos["patients"], repos["doctors"]
        self.appointments, self.invoices = repos["appointments"], repos["invoices"]
        self.gateway, self.bus = gateway, bus or EventBus()

    def _get(self, repo: Repository, id: int) -> dict:
        item = repo.get(id)
        if item is None:
            raise NotFoundError(f"{repo.table[:-1]} {id} not found")
        return item

    # ---- Module 1: Patients ----
    def register_patient(self, name: str, phone: str, age: int) -> dict:
        if not name.strip():
            raise ValueError("Name is required")
        if not re.fullmatch(r"01\d{9}", phone):
            raise ValueError("Phone must be 11 digits starting with 01")
        if not 0 <= age <= 120:
            raise ValueError("Age must be between 0 and 120")
        return self.patients.add(name=name.strip(), phone=phone, age=age)

    # ---- Module 2: Doctors ----
    def add_doctor(self, name: str, specialty: str, fee: float) -> dict:
        if fee <= 0:
            raise ValueError("Fee must be positive")
        return self.doctors.add(name=name, specialty=specialty, fee=fee)

    # ---- Module 3: Appointments ----
    def book(self, patient_id: int, doctor_id: int, slot: str) -> dict:
        patient = self._get(self.patients, patient_id)
        doctor = self._get(self.doctors, doctor_id)
        if datetime.fromisoformat(slot) <= datetime.now():
            raise ValueError("Slot must be in the future")
        if self.appointments.find(doctor_id=doctor_id, slot=slot, status="BOOKED"):
            raise ConflictError("Slot already booked")
        appt = self.appointments.add(patient_id=patient_id, doctor_id=doctor_id, slot=slot)
        amount = fee_strategy_for(patient["age"]).compute(doctor["fee"])
        invoice = self.invoices.add(appointment_id=appt["id"], amount=amount)
        self.bus.publish("appointment_booked", {
            "phone": patient["phone"], "doctor": doctor["name"], "slot": slot,
            "amount": amount})
        return {**appt, "invoice": invoice}

    def cancel(self, appointment_id: int) -> dict:
        appt = self._get(self.appointments, appointment_id)
        if appt["status"] != "BOOKED":
            raise ConflictError("Appointment is not active")
        patient = self._get(self.patients, appt["patient_id"])
        self.bus.publish("appointment_cancelled", {"phone": patient["phone"], "slot": appt["slot"]})
        return self.appointments.update(appointment_id, status="CANCELLED")
