# orko-backend

Tiny starter for ORKO API.

## Quickstart
```bash
python -m venv .venv
# Windows: .\.venv\Scripts\activate
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
# Open http://localhost:8000/healthz
```
