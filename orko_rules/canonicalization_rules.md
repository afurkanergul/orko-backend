\# Canonicalization Rules



\## Purpose



Enforce strict, global naming and structural patterns:



\- Domains

\- Actions

\- Parameters

\- Entities

\- Config keys



---



\## Canonical Name Structure



\- Domains: `snake\_case`, singular where possible. Example: `portfolio`, `execution`, `pricing`.

\- Actions: `snake\_case`, verb-first where possible. Example: `create\_order`, `cancel\_order`.

\- Parameters: `snake\_case`, descriptive. Example: `instrument\_id`, `tenant\_id`, `risk\_score`.



Aider MUST detect:



\- Inconsistent naming of the same concept across files.

\- Overloaded names used for different concepts.



---



\## Canonical Lineage Rules



For every domain/action/parameter, Aider MUST:



1\. Identify its canonical definition location (Pattern Brain or core models).

2\. Build a lineage:

&nbsp;  - Where it is defined.

&nbsp;  - Where it is consumed.

&nbsp;  - Where it is persisted (DB).

&nbsp;  - Where it is exposed (APIs, UI).



3\. Ensure ALL references share exactly the same spelling and conceptual meaning.



---



\## Conflict Detection



Aider MUST flag:



\- Same name used for different concepts.

\- Different names used for the SAME concept.

\- Multiple canonical definitions of the same concept.



For each conflict, Aider MUST:



\- Propose a single canonical name.

\- Suggest patches to align all references.

\- Provide risk assessment (e.g., “high risk if renamed incorrectly”).



---



\## Multi-Industry \& Multi-Tenant Constraints



\- Names MUST NOT embed industry-specific terms unless absolutely necessary.

\- Tenancy-related fields (e.g., `tenant\_id`, `org\_id`) MUST be consistent everywhere.

\- Aider must avoid turning ORKO into a single-industry system.



---



\## Reporting



For canonicalization issues, Aider MUST provide:



\- Category: `canonicalization\_error` / `naming\_conflict`

\- Files and line numbers

\- Suggested canonical name

\- Exact before/after name mapping

\- Suggested patches (multi-file allowed)



