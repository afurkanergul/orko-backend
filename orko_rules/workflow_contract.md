# Workflow Contract for ORKO (External Diagnostics via Aider)

## Purpose

Define how Aider must analyze and validate ORKO workflows without embedding diagnostics into ORKO itself.

ORKO is the workflow engine.  
Aider is the external auditor and fixer.

## Workflow Definition Expectations

A workflow is any sequence of steps that:

- Accepts an input (JSON, API request, message).
- Performs validations and transformations.
- Executes actions (e.g., parsing, evaluation, model calls, storage).
- Produces outputs (responses, events, database writes, logs).

## Required Properties for Each Workflow

Aider should expect or infer for each workflow:

- Name / identifier.
- Domain and action (where applicable).
- Input schema reference.
- Output schema reference.
- Pre-conditions and post-conditions.
- Error handling strategy.
- Observability hooks (logging/metrics/traces).

## Workflow Alignment Checks

Aider MUST perform:

1. **Input alignment**
   - Workflow entrypoints use schemas defined in `schema_contract`.
   - All used parameters exist in canonical definitions.

2. **Step-by-step lineage verification**
   - Map data as it flows between:
     - Parser.
     - Validator.
     - Business logic.
     - Evaluator.
   - Ensure nothing is silently dropped or added without schema support.

3. **Evaluator–Parser–Workflow lineage**
   - Evaluators only consume well-defined outputs of parsers and workflows.
   - Workflows do not call evaluators with incomplete payloads.
   - All evaluator outputs are either used or explicitly discarded.

4. **Cross-language workflow validation**
   - Backend endpoints ↔ frontend calls.
   - Worker jobs ↔ database operations.
   - Config-driven workflows ↔ implementation.

## Multi-Step Workflow Validation

Aider should construct a workflow graph and verify:

- There is a clear path from input to output for each workflow.
- Loops and retries are safe and bounded.
- Critical steps have error handling and logging.
- Unsupported states/transitions are flagged.

## Risk Scoring

For each workflow, Aider must compute a risk score based on:

- Number and severity of mismatches.
- Missing validation steps.
- Missing logging on critical edges.
- Presence of TODOs or commented-out guards.

Scores: `low`, `medium`, `high`, `critical`.

## Reporting

For each high/critical workflow issue, Aider must:

- Provide:
  - Workflow name.
  - Files and line numbers.
  - Description of problem.
  - Recommended fix (may include code).
- Optionally propose multi-file patches that:
  - Add missing validations.
  - Align schemas and parameters.
  - Introduce logging and guards.

## Multi-Tenant and Multi-Industry Rules

- Workflows must NOT hardcode a single industry.
- Aider should detect:
  - References that make flows industry-specific without configuration.
  - Missing tenant boundaries.

Aider should recommend parameterizing such assumptions.
