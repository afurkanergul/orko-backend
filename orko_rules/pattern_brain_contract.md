\# Pattern Brain Contract (Maximum-Level, External Diagnostics Only)



\## Core Principles



1\. Pattern Brain is an INTERNAL, CLEAN CONTRACT LAYER.

2\. Pattern Brain DOES NOT run diagnostics.

3\. Aider + Git + GitHub is the ONLY diagnostics engine.

4\. Pattern Brain defines expected patterns, invariants, and lineage across the entire repo.

5\. ORKO is multi-industry and multi-tenant. No single-industry bias is allowed.



---



\## Supported Domains and Languages



\- Multi-industry by design (finance, agriculture, logistics, e-commerce, healthcare, etc.).

\- Multi-language code and config:

&nbsp; - Python (backend, scripts).

&nbsp; - JavaScript / TypeScript (frontend, tools).

&nbsp; - JSON (schemas, config).

&nbsp; - YAML (config, workflows).

&nbsp; - Go (future backend modules or tools).



Aider must treat all of these as first-class when running diagnostics.



---



\## Semantic Graph Expectations



When Aider runs diagnostics, it MUST construct a conceptual semantic graph of the repo:



\- Nodes:

&nbsp; - Files

&nbsp; - Modules

&nbsp; - Classes

&nbsp; - Functions

&nbsp; - Endpoints (HTTP routes)

&nbsp; - Schemas / DTOs

&nbsp; - DB tables and columns

&nbsp; - Config entries

&nbsp; - Domains, actions, parameters



\- Edges:

&nbsp; - “calls” / “uses”

&nbsp; - “implements”

&nbsp; - “depends on”

&nbsp; - “validates”

&nbsp; - “is defined by”

&nbsp; - “is consumed by”



The semantic graph MUST support reasoning about:



1\. Cross-file consistency.

2\. Cross-language coherence (e.g., backend FastAPI routes ↔ frontend API clients).

3\. Schema → DB → code alignment.

4\. Parser → Evaluator → Workflow lineage.



---



\## Cross-Domain Pattern Invariants



Aider MUST enforce these invariants during diagnostics:



1\. \*\*Canonical Domain Model\*\*

&nbsp;  - Every business domain MUST have:

&nbsp;    - A canonical name (e.g., `trading`, `orders`, `users`, `portfolios`).

&nbsp;    - A clear set of actions (e.g., `create\_order`, `cancel\_order`, `evaluate\_risk`).

&nbsp;    - A defined parameter set with types and constraints.



2\. \*\*Non–Industry-Specific\*\*

&nbsp;  - Names and patterns MUST NOT hard-code a single industry.

&nbsp;  - Example: prefer `instrument` over `grain`, `asset` over `corn`.



3\. \*\*Multi-Tenant Safety\*\*

&nbsp;  - No hard-coded tenant IDs.

&nbsp;  - Tenant-specific logic must be gated and configurable.

&nbsp;  - Access control and separation of tenant data must be respected in patterns.



4\. \*\*Observability\*\*

&nbsp;  - Key flows must expose:

&nbsp;    - Logging hooks

&nbsp;    - Metrics hooks

&nbsp;    - Tracing hooks (even if not fully implemented yet)

&nbsp;  - Aider should flag missing observability anchors in critical paths.



---



\## Workflow–Schema–Parameter Alignment



For each workflow, Aider MUST verify:



1\. The workflow steps reference only existing, canonical domains and actions.

2\. Every input/output parameter in the workflow:

&nbsp;  - Exists in schemas.

&nbsp;  - Is used consistently in code and DB.

3\. Evaluator, parser, and workflow definitions share the SAME domain/action/parameter names.



If any mismatch exists, Aider MUST:

\- Mark it as a high-severity issue.

\- Suggest canonical renaming or schema updates.

\- Include line numbers, files, and a suggested patch.



---



\## Full-Repo Correlation Constraints



Aider MUST check correlations across:



\- `orko-backend/`

\- `orko-frontend/`

\- `pattern\_brain/`

\- `orko\_rules/`

\- Config files (YAML, JSON)

\- GitHub workflows



It MUST detect when:



1\. A route exists with no matching schema.

2\. A schema exists with no matching DB mapping.

3\. A DB column exists with no schema field or code usage.

4\. A workflow step references a non-existent domain/action/parameter.

5\. Evaluator or parser logic diverges from workflow contracts.



---



\## Internal Cleanliness Rule



Pattern Brain is ONLY a set of contracts and invariants. It MUST NOT:



\- Contain diagnostic engines.

\- Contain complex execution logic.

\- Duplicate Aider’s functionality.



Aider uses this contract as the authoritative reference for what “correct” means across the repo.



