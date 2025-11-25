# ORKO Repository Overview

## Repository Tree (Top-Level)

- orko-backend/
- orko-frontend/
- orko_rules/
- alembic/
- alembic.ini
- Makefile
- README.md
- requirements.txt
- runtime.txt
- render.yaml
- .env.example
- .gitignore
- dummy_rebuild.txt
- ORKO_Inbox/
- diagnostics/  *(created by diagnostics engine)*
- .github/
- orko-infra/

## Missing or Surprising Folders

**Expected folders present:**
- orko-backend/
- orko-frontend/
- orko_rules/

**Surprising folders:**
- ORKO_Inbox/ (purpose unclear, not mentioned in contracts)
- orko-infra/ (may be for infrastructure, not referenced in rule contracts)
- alembic/ (expected for DB migrations, but not mentioned in contracts)

**No expected folders are missing.**
