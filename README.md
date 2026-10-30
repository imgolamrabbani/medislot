# MediSlot — Clinic Appointment & Billing System

[![CI](https://github.com/imgolamrabbani/medislot/actions/workflows/ci.yml/badge.svg)](https://github.com/imgolamrabbani/medislot/actions/workflows/ci.yml)

CSE 3206 (Software Engineering Sessional) — Lab 6 / CO4 project.
A small but complete clinic system built with **FastAPI + SQLite**, developed with TDD,
design patterns, Selenium, GitHub Actions CI and a feature-branch Git workflow.

## Modules
| # | Module | What it does |
|---|--------|--------------|
| 1 | Patients | Register patients with validated phone/age |
| 2 | Doctors | Add doctors with specialty and consultation fee |
| 3 | Appointments | Book / cancel slots, prevents double booking |
| 4 | Billing | Age-based fee (Strategy) and bKash payment (Adapter) |
| 5 | Notifications | Patient messages on booking/cancel (Observer + Factory) |

## Design Patterns
| Pattern | Category | Where |
|---------|----------|-------|
| Factory | Creational | `NotifierFactory` in `app/notifications.py` |
| Adapter | Structural | `BkashAdapter` in `app/billing.py` |
| Strategy | Behavioral | `FeeStrategy` family in `app/billing.py` |
| Observer | Behavioral | `EventBus` in `app/events.py` |

UML class diagram: [`docs/uml.png`](docs/uml.png)

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
- Web UI: http://127.0.0.1:8000
- Swagger UI (OpenAPI docs): http://127.0.0.1:8000/docs

## Testing
```bash
pytest --cov=app --cov-report=term-missing   # all tests + coverage
pytest -m ui                                  # Selenium browser test only
```
CI (GitHub Actions) runs the same suite on every push and pull request.

## Git Workflow
- Branches: `feature/<module>`, `ci/<topic>`, `docs/<topic>`
- Commits follow Conventional Commits: `test:`, `feat:`, `refactor:`, `ci:`, `docs:`
- Every change goes through a Pull Request; CI must pass before merge.

## AI Usage Statement
An AI assistant was used for drafting code and documentation. All code was reviewed,
run and tested by the author, who can explain every part.
