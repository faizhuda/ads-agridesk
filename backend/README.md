# Agridesk Backend

## Completed Core Features

- JWT authentication + role-based authorization
- Surat workflow: create -> dosen sign -> admin approve -> verify hash
- Signature persistence to `signatures` table
- QR verification generation on admin approval
- PDF generation on admin approval
- Audit trail persistence to `audit_logs` table
- Structured HTTP request logging with request id
- Health and readiness endpoints (`/health`, `/ready`)
- In-memory IP rate limiting with configurable thresholds
- Alembic migration management
- Pytest unit + integration tests

## Setup Environment

1. Copy `.env.example` to `.env`
2. Fill required values:
   - `DATABASE_URL`
   - `JWT_SECRET_KEY`
   - `AGRIDESK_HASH_SECRET`
   - `AGRIDESK_RATE_LIMIT_ENABLED`
   - `AGRIDESK_RATE_LIMIT_WINDOW_SECONDS`
   - `AGRIDESK_RATE_LIMIT_REQUESTS`

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run API

```bash
uvicorn app.main:app --reload
```

## Database Migration (Alembic)

```bash
alembic upgrade head
```

## Current Migration Revisions

- `20260301_0001`: required columns (`is_external`, timestamps)
- `20260301_0002`: `signatures` table + surat `pdf_path` and `qr_path`
- `20260301_0003`: `audit_logs` table

## Run Tests

```bash
pytest -q
```

## Run Tests with Coverage

```bash
pytest -q --cov=app --cov-report=term-missing --cov-report=xml
```
