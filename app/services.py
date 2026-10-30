"""Business logic for all modules. Dependencies are injected (easy to mock)."""
import re

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
