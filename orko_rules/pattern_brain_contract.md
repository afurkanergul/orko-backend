# Pattern Brain Contract (External Diagnostics via Aider ONLY)

## Core Principles

1. Pattern Brain is an internal ORKO concept for:
   - Defining cross-domain patterns.
   - Encoding invariants and expectations.
   - Describing how workflows, schemas, evaluators, parsers, and parameters must align.
2. Pattern Brain **does NOT perform diagnostics itself.**
   - All diagnostics are executed externally by **Aider + Git + GitHub**.
   - ORKO remains a clean execution and workflow engine.
3. Aider is the single diagnostics engine responsible for:
   - Reading these contracts and rules.
   - Building semantic and structural understanding of the repo.
   - Finding violations.
   - Proposing and applying fixes.

## Cross-Domain Pattern Invariants

Aider MUST assume and enforce these invariants across all languages (Python, JS/TS, JSON, YAML, and future GO):

1. Every domain, action, and parameter has a **single canonical definition**.
2. Canonical definitions must appear in:
   - A central canonical registry (YAML/JSON/TOML file when present).
   - Backend schemas and validator classes.
   - Evaluator and parser code.
   - Workflow definitions (state machines, orchestration logic).
3. For any entity `(domain, action, parameter)`:
   - **Name** must be consistent across backend, frontend, schemas, docs, tests, and configuration.
   - **Type** and **allowed values** must match wherever referenced.
   - **Semantics** (what it means) must not conflict across files.

## Semantic Lineage Expectations

Aider MUST build and reason about **lineage chains**:

- Input → Parsing → Validation → Business Logic → Evaluator → Output

For each lineage, Aider should:

1. Map input fields to:
   - Request payloads (FastAPI models).
   - Frontend forms / API calls.
   - Database models (where applicable).
   - Evaluator inputs.
2. Check that:
   - No field appears in the evaluator that is missing from schema or parser.
   - No field appears in schema that is never parsed, validated, or used.
3. Detect and report:
   - Missing links in the chain.
   - Conflicting types between steps.
   - Conflicting naming between steps.

## Workflow–Schema–Parameter Alignment Rules

1. Every workflow step must reference only canonical domains, actions, and parameters.
2. Each workflow must specify:
   - Expected input structure.
   - Transformation logic.
   - Output structure.
3. Aider must:
   - Identify workflows that use undefined or deprecated parameters.
   - Identify workflows with unclear or mismatched preconditions and postconditions.
   - Highlight missing validation steps between parsing and evaluator.

## Observability Expectations

Pattern Brain requires that diagnostics encourage observability:

1. Aider should look for:
   - Logging hooks at key workflow boundaries.
   - Error handling around external calls.
   - Structured logs (JSON) for core events when present.
2. Aider reports when:
   - A critical workflow has no logging.
   - A critical schema/evaluator mismatch is not guarded.
   - A critical API endpoint lacks validation.

## Full Repo Correlation Constraints

Aider MUST treat the repo as a single correlated system, not isolated files:

1. Build a semantic graph of:
   - Domains, actions, parameters.
   - Schemas, validators, models.
   - Parsers, evaluators, workflows.
   - Backend and frontend API layers.
2. Use this graph to:
   - Detect dangling definitions.
   - Detect inconsistent naming.
   - Detect missing alignments.
   - Score risk per node and per edge.

## Multi-Industry and Multi-Tenant Requirements

1. All patterns must be **industry-agnostic**:
   - No hard-coded assumptions tied to a single domain (e.g., agriculture only).
2. Multi-tenant safety:
   - Aider should flag patterns where tenant isolation might be broken (shared IDs, no tenant filter, etc.).
   - Aider should encourage boundaries: tenant_id, organization_id, or similar attributes.

## Relationship to Aider Tasks

- All Aider diagnostic tasks MUST:
  - Load and respect this contract.
  - Treat these rules as **hard constraints** unless clearly documented as TODO.
  - Never move diagnostics logic into ORKO itself.
- ORKO is the execution engine; Aider is the external doctor and auditor.
