\# Schema Contract



\## Goals



1\. Enforce strict alignment between:

&nbsp;  - JSON/YAML schemas

&nbsp;  - Python/Go data models

&nbsp;  - DB schemas (PostgreSQL)

&nbsp;  - Frontend types (TS/JS)

2\. Avoid schema drift.

3\. Support multi-tenant, multi-industry, multi-language environments.



---



\## Schema Sources



Aider MUST treat the following as schema sources:



\- Backend:

&nbsp; - Pydantic models (FastAPI request/response models)

&nbsp; - ORM models (e.g., SQLAlchemy) mapping to PostgreSQL (`orko\_ai`)

\- DB:

&nbsp; - Table definitions and migrations referencing `orko\_ai`

\- Frontend:

&nbsp; - TypeScript interfaces / types representing API payloads

\- Config:

&nbsp; - JSON/YAML schema definitions



---



\## Schema → DB → Code Alignment Rules



For each entity:



1\. Every field in a schema must:

&nbsp;  - Map to a DB column, OR

&nbsp;  - Be explicitly documented as virtual/derived.

2\. Every DB column must:

&nbsp;  - Map to a schema field, OR

&nbsp;  - Be explicitly marked as internal/technical (e.g., audit fields).

3\. Types must be consistent or safely coercible:

&nbsp;  - Example: `integer` in DB ↔ `int` in Python ↔ `number` in TS.

4\. Nullability and optionality must align:

&nbsp;  - `NOT NULL` in DB MUST NOT be optional in the schema without a default.

5\. Multi-tenant fields:

&nbsp;  - Tenant identifiers must be consistently named and typed.



Aider MUST flag any deviation as a schema alignment issue.



---



\## Schema Validation Rules



Aider diagnostics MUST:



\- Ensure every request/response body used by FastAPI routes references a schema.

\- Ensure every public API is represented in:

&nbsp; - Backend models

&nbsp; - Frontend types

&nbsp; - Pattern Brain contracts, where relevant

\- Check that JSON/YAML configuration defining schemas matches:

&nbsp; - Actual code

&nbsp; - DB migrations



---



\## Reporting Requirements



Aider MUST output for each detected issue:



\- Category: `schema\_mismatch` / `schema\_drift` / `schema\_missing`

\- Files and line numbers

\- Expected vs actual schema definition

\- Proposed fix suggestion (including patch snippets)

\- Severity (e.g., `high` if it can cause runtime breakage)





