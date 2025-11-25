# Canonicalization Rules for ORKO

## Purpose

Ensure strict canonical naming and structure for:

- Domains
- Actions
- Parameters
- Workflow names
- Schema names
- Evaluator and parser identifiers

Aider uses these rules to detect inconsistencies and propose fixes.

## Canonical Naming Rules

1. Domains:
   - Format: `snake_case` or `kebab-case` in code, configurable, but consistent.
   - Must not include industry-specific suffixes (avoid `grain_trading_only` style names).

2. Actions:
   - Verb-noun pattern where possible: `create_order`, `evaluate_parser`, etc.
   - Same action name across backend, frontend, and configs.

3. Parameters:
   - Clear, descriptive names.
   - Avoid synonyms for the same concept in different parts of the system.

4. Canonical registry:
   - Where present (e.g., YAML or JSON), it is the single ground truth.
   - All code and workflows must align with it.

## Canonicalization Checks

Aider MUST:

1. Identify all occurrences of domains/actions/parameters across:
   - Backend Python.
   - Frontend JS/TS.
   - Config files (JSON/YAML/TOML).
   - Rule files and docs.

2. Group them into canonical entities:
   - Same name, same type, same meaning.

3. Detect:
   - Naming drift (e.g., `tenant_id` vs `tenantId` vs `org_id`).
   - Semantic drift (same name used for different meanings).

4. Propose:
   - Concrete rename strategies.
   - Code patches for safe renaming.
   - Updates in tests and documentation.

## Canonical Lineage

For each canonical entity, Aider constructs a lineage:

- Canonical definition → schemas → parsers → workflows → evaluators → outputs → logs

Any missing link or mismatch becomes a diagnostic.

## Multi-Tenant and Multi-Company Canonicalization

- Entities related to tenant or company boundaries must be explicit.
- Aider should detect ambiguous names that risk cross-tenant leakage.
- Recommended pattern: `tenant_id` or `customer_id` consistently throughout.

## Enforcement

When Aider applies autofixes:

- It must:
  - Follow these rules.
  - Update all references in a single coherent patch where possible.
  - Re-run checks to confirm the repo is in a more canonical state than before.
