# ORKO Command Parser — Architecture & API (Step 6 Final)

## 1. Purpose
The ORKO Command Parser converts natural-language commands into structured,
industry-agnostic intents. It supports multi-domain classification, action extraction,
slot-filling, guardrails, reasoning logs, rate limits, and async workflow triggering.

## 2. High-Level Flow
User Command →
  ParserEngine →
    AIParser (LLM-based) →
      IntentMapper →
        Confirmation / Guardrails →
          TriggerQueue (Celery/Redis) →
            WorkflowOrchestrator →
              DLQ or Success

## 3. Components

### ParserEngine
- Entry point: `parse_command(text, context)`
- Responsibilities:
  - Load guardrails and destructive verbs.
  - Invoke AIParser.
  - Add reasoning traces.
  - Enforce confirmation rules.
  - Emit audit + parser_logs.

### AIParser
- LLM-powered structured JSON output.
- Multi-domain support (finance, trading, HR, IT, CS, operations, logistics, etc.)
- Few-shot templates.
- Outputs:
  - `domain`
  - `action`
  - `parameters`
  - `context` (e.g. `{ confidence, reasoning_trace }`)

### IntentMapper
- Maps `domain` + `action` → `workflow_name`.
- Defined in: `backend/app/services/workflow/intent_map.json`.

### TriggerQueue
- Celery-based async queue.
- Produces deterministic `trigger_job_id`.
- DLQ support for workflow failures.

### Guardrails
- Config:
  - `backend/app/services/parsing/config/intent_guardrails.json`
  - `backend/app/services/parsing/config/guardrails.json`
- Concepts:
  - `destructive_verbs`
  - `requires_confirmation` logic

### Rate Limiting
- Per-user/org limit (default 5/min).
- Redis-backed `TriggerRateLimiter`.

### Reasoning Logs
- Masked reasoning (names/emails/phones).
- Stored in `parser_logs` table.

## 4. APIs

### POST /trigger
**Input:**
- `command`
- `org_id`
- `source`, `channel`
- `request_id`

**Behavior:**
- Parse → confidence-gate → enqueue trigger.

**Responses:**
- `queued`
- `requires_review` (low confidence)
- `429` (rate limit)

### GET /parser/metrics/latest
Returns latest evaluation metrics for dashboards.

## 5. Multi-Industry Model
ORKO is not tied to any single industry.

Supported domains include (but are not limited to):

- `trading`
- `logistics`
- `finance`
- `hr`
- `it_ops`
- `customer_support`
- `operations`
- `analytics`
- `legal`

…and it is extendable with new domains.

## 6. Data Stores
- `parser_logs` (reasoning)
- `parser_metrics` (evaluation)
- Action whitelist/blacklist (JSON-level governance)
- DLQ logs

## 7. Security
- JWT auth
- RBAC (admin can see `debug_reasoning`)
- Safe reasoning (PII masked)
- Destructive verb confirmation

## 8. Observability
- Parser latency
- Queue latency
- DLQ triggers
- Parser accuracy metrics
