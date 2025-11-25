\# Workflow Contract



\## Purpose



Define how workflows must align with:



\- Parser behavior

\- Evaluator behavior

\- Schemas

\- DB

\- Frontend usage



Aider uses this to validate \*\*end-to-end lineage\*\* from input → parser → evaluator → output.



---



\## Workflow Definition Expectations



Workflows may be represented as:



\- Python orchestration code

\- YAML/JSON workflow files

\- Pattern Brain contract entries

\- Documentation in Markdown



For each workflow, Aider MUST be able to determine:



1\. Input domains, actions, parameters.

2\. Order of steps.

3\. Decision branches / conditions.

4\. Expected outputs and side-effects.



---



\## Lineage: Input → Parser → Evaluator → Output



Aider MUST verify that:



1\. Parser:

&nbsp;  - Identifies domains, actions, parameters according to canonical definitions.

&nbsp;  - Outputs structures that match the schemas.



2\. Evaluator:

&nbsp;  - Consumes the parser output WITHOUT implicit renaming or hidden assumptions.

&nbsp;  - Produces results that map back to canonical domain concepts.



3\. Workflow:

&nbsp;  - Orchestrates parser and evaluator in a clear sequence.

&nbsp;  - Uses canonical names consistently at each step.



Any mismatch (e.g., parser uses `order\_type` while evaluator uses `trade\_type`) MUST be:



\- Reported as a `workflow\_alignment\_error` AND `canonicalization\_error`.

\- Accompanied by suggested renaming or refactoring.



---



\## Multi-Step Workflow Validation



For every workflow Aider analyzes:



\- Ensure all steps:

&nbsp; - Are reachable (no dead flows) OR explicitly documented as deprecated.

&nbsp; - Have clear preconditions and postconditions.

\- Validate that:

&nbsp; - Every step’s inputs are produced by previous steps or external sources.

&nbsp; - Every step’s outputs are either consumed or explicitly final.



---



\## Multi-Language Cross-Workflow Checks



Aider MUST validate:



\- Backend workflow ↔ Frontend calls:

&nbsp; - Every frontend call corresponds to a backend route.

&nbsp; - Payload shapes match the schema contract.

\- Backend ↔ Config:

&nbsp; - Workflow names and step identifiers referenced in config exist in code.



---



\## Reporting



For each workflow issue, Aider MUST provide:



\- Category: `workflow\_alignment\_error`, `dead\_step`, `missing\_step`, etc.

\- Files, line numbers.

\- Impacted domains/actions/parameters.

\- Severity and suggested fix.



