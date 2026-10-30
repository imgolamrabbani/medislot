# MediSlot

Clinic appointment & billing system — CSE 3206 Lab 6 (CO4) project.

## Modules
Patients, Doctors, Appointments, Billing, Notifications.

## Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload      # UI: /   Swagger: /docs
```

## Testing
```bash
pytest --cov=app --cov-report=term-missing   # all tests + coverage
pytest -m ui                                  # Selenium browser test only
```
