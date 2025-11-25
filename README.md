<<<<<<< HEAD
\# ORKO – External Diagnostics via Aider + Git + GitHub



\- Backend: Python + FastAPI (`orko-backend/`)

\- Frontend: TBD (`orko-frontend/`)

\- Pattern Brain: internal contracts only, NO diagnostics (`pattern\_brain/`)

\- Diagnostics Engine: \*\*Aider + Git + GitHub only\*\*

\- Rules: `orko\_rules/` (multi-industry, multi-tenant, maximum-level diagnostics)



=======
# ORKO Backend

![ORKO Backend CI](https://github.com/afurkanergul/orko-backend/actions/workflows/ci.yml/badge.svg)

Tiny starter for ORKO API — the foundation of the ORKO automation system.  
Includes FastAPI, PostgreSQL, and CI validation for clean, multi-tenant backend development.

---

## 🚀 Quickstart

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
# Open http://localhost:8000/healthz

## 🧩 Database Documentation

- [View ORKO Database Schema](./docs/db_schema.md)
- [Download ERD Image](./docs/orko_db_2025_11_01.png)
>>>>>>> 0e617b2fa638697bd42e9a900ed3aea7e4b9e620
