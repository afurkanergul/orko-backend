# Schema Contract for ORKO (External Diagnostics via Aider)

## Scope

This contract defines how Aider must reason about schemas across:

- Backend (FastAPI, Pydantic models, dataclasses).
- Database models (SQLAlchemy or equivalents).
- JSON/YAML configuration files.
- Frontend API payloads (TS types, interfaces, Zod schemas where present).

## Core Rules

1. Every input/output handled by ORKO MUST have a **schema**.
2. Schemas MUST be the single source of truth for:
   - Field names.
   - Field types.
   - Required vs optional.
   - Default values.
   - Enum/choice values when applicable.

## Alignment Expectations

Aider MUST verify:

1. **Schema ↔ Parser alignment**
   - All fields parsed from requests or files are defined in a schema.
   - Parsers do not accept fields that are missing in schema definitions.
   - Types match (e.g., string vs int vs list).

2. **Schema ↔ Evaluator alignment**
   - Evaluators do not reference fields not guaranteed by the schema.
   - Evaluators handle optional vs required fields correctly.
   - Risky assumptions are flagged (e.g., unguarded `field["key"]` when not required).

3. **Schema ↔ Database alignment**
   - When DB models exist, columns match schema fields:
     - Type compatibility.
     - Nullability vs required.
     - Length/constraints vs enum/choices.
   - Orphan columns / orphan schema fields are highlighted.

4. **Schema ↔ Frontend alignment**
   - Frontend TS/JS types match backend schema:
     - Name.
     - Type.
     - Optionality.
   - Aider reports mismatches as risks for runtime bugs.

## Error Categories to Report

For each schema-related problem, Aider MUST categorize it into:

- `SchemaMismatch`
- `SchemaParserMismatch`
- `SchemaEvaluatorMismatch`
- `SchemaDBMismatch`
- `SchemaFrontendMismatch`
- `MissingSchemaDefinition`
- `OutdatedSchemaDefinition`

Each finding should include:

- File path(s).
- Line numbers.
- Severity: `low`, `medium`, `high`, `critical`.
- Suggested fix (concrete).

## Multi-Language Considerations

- Python: Pydantic models, dataclasses, TypedDicts.
- JS/TS: types, interfaces, Zod schemas, Yup schemas.
- JSON/YAML: explicit schema files or config with implied schema.

Aider must construct a **unified schema view** across languages.

## Performance & Evolution

- Aider should flag duplicated schemas that drift over time.
- Aider may recommend refactoring towards a single canonical location for schema definitions.

## Relationship to Other Contracts

- This file is tightly connected to:
  - `pattern_brain_contract.md` (lineage and invariants).
  - `workflow_contract.md` (how schemas are used in workflows).
  - `canonicalization_rules.md` (naming and IDs).

Aider should cross-reference all three when performing diagnostics.
