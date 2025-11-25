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
