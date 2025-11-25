# Aider Settings for ORKO Diagnostics

## Default Model

- Use: `gpt-4.1`
- Invocation example:
  - `aider --model gpt-4.1`

## Patch Style

- Balanced:
  - Avoid hyper-aggressive refactors.
  - Prefer minimal, well-scoped, high-quality changes.

## Languages of Interest

- Python (FastAPI backend).
- JavaScript/TypeScript (frontend).
- JSON/YAML (configs and schema).
- Go (future).

## Repo Structure Assumptions

- Single repo containing:
  - `orko-backend/`
  - `orko-frontend/`
  - `orko_rules/`
  - Pattern Brain related files (to be added)
- Backend entrypoint: `orko-backend/app/main.py`
- Dev server: `uvicorn app.main:app --reload` at `http://localhost:8000`

## Diagnostics Philosophy

- ORKO is NOT a diagnostics engine.
- Aider + Git + GitHub form the external diagnostics system.
- All deep analysis, semantic graphs, AST reasoning, and risk scoring happen in Aider.

## Output Formats

Aider should produce:

1. **JSON**:
   - Machine-readable reports for future automation.
2. **Markdown**:
   - Human-friendly diagnostics summaries for PR comments.

## Safety and Guardrails

- No destructive actions without clear justification.
- Prefer PR-based autofixes:
  - Create branches like `aider/fix-<short-description>`.
  - Open PRs against `dev`.

## Working Directory

- Always start Aider from the repo root:
  - `C:\Users\AhmetErgul\Downloads\ORKO_Step1-1_starter`
