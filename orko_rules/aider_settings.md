\# Aider Settings \& Master Instructions (Maximum-Level Diagnostics)



\## Core Principles



1\. ORKO does NOT implement diagnostics internally.

2\. Aider + Git + GitHub IS the diagnostics engine.

3\. All diagnostics are external, driven by Aider tasks and GitHub workflows.

4\. ORKO must remain multi-industry, multi-tenant, and production-grade.



---



\## General Behavior for Aider



When running in this repo, Aider MUST:



1\. Read and obey all rules in:

&nbsp;  - `orko\_rules/pattern\_brain\_contract.md`

&nbsp;  - `orko\_rules/schema\_contract.md`

&nbsp;  - `orko\_rules/workflow\_contract.md`

&nbsp;  - `orko\_rules/canonicalization\_rules.md`

&nbsp;  - `orko\_rules/aider\_settings.md` (this file)



2\. Treat these files as \*\*hard constraints\*\*.



3\. Always:

&nbsp;  - Explain the reasoning behind diagnostics.

&nbsp;  - Return structured outputs:

&nbsp;    - JSON diagnostics block.

&nbsp;    - Markdown summary (for PR comments).



---



\## Maximum-Level Diagnostics Capabilities



Aider MUST attempt to:



\- Build a semantic graph across:

&nbsp; - `orko-backend/`

&nbsp; - `orko-frontend/`

&nbsp; - `pattern\_brain/`

&nbsp; - Config files (JSON/YAML)

&nbsp; - GitHub workflows

\- Perform multi-language AST-style analysis for:

&nbsp; - Python

&nbsp; - JS/TS

&nbsp; - JSON

&nbsp; - YAML

&nbsp; - (Go – where present)

\- Cross-file semantic consistency mapping:

&nbsp; - Schema ↔ DB ↔ Code ↔ Frontend ↔ Workflows

\- Verify:

&nbsp; - Evaluator → Parser → Workflow lineage

&nbsp; - Canonical domain/action/parameter lineage

\- Compute risk scores for:

&nbsp; - Inconsistencies

&nbsp; - Complexity

&nbsp; - Potential breakages



---



\## Output Format Requirements



For \*\*every diagnostics run\*\*, Aider MUST output:



1\. A JSON block (in a fenced ```json code block) with:

&nbsp;  - `summary`

&nbsp;  - `issues` (list)

&nbsp;    - `id`

&nbsp;    - `category`

&nbsp;    - `severity`

&nbsp;    - `description`

&nbsp;    - `files`

&nbsp;    - `line\_numbers`

&nbsp;    - `proposed\_fix\_summary`

&nbsp;  - `risk\_score\_overall` (0–100)

&nbsp;  - `recommended\_next\_actions` (list)

2\. A Markdown report suitable for PR comments:

&nbsp;  - Executive summary

&nbsp;  - Risk breakdown

&nbsp;  - Key issues

&nbsp;  - Recommended fixes



---



\## Auto-Fix Behavior



When explicitly instructed by a task:



\- Aider MAY generate patches across multiple files.

\- Patches MUST:

&nbsp; - Respect canonicalization rules.

&nbsp; - Maintain schema/workflow alignment.

&nbsp; - Be minimal but complete.

\- After applying patches, Aider MUST:

&nbsp; - Re-run diagnostics in a \*\*“post-fix check”\*\* mode.

&nbsp; - Confirm that high-severity issues are reduced or resolved.



---



\## Safety \& Destructive Actions



Aider MUST:



\- Avoid destructive operations (e.g., deleting large file sets) unless explicitly asked.

\- Always show patches before applying (via Git diffs).

\- Prefer refactoring over “quick hacks”.



