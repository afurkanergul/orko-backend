# ORKO Observability Suggestions v7

Generated at: Thu Nov 20 20:51:48 2025

## 1. Domain-level Suggestions
### Domain: marketing
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: general
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: general_admin
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: knowledge_work
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: operations
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: logistics
- F1: 0.27
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: sales
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: customer_support
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: trading
- F1: 0.25
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: hr
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: retail
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: legal
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: finance
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: devops
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: it_ops
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: procurement
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: manufacturing
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: docs
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: healthcare_admin
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: energy
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

### Domain: analytics
- F1: 0.00
- Suggested actions:
  - Add more labeled examples for this domain.
  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.
  - Tighten or expand guardrails / prompts for this domain.

## 2. Guardrail & Safety Suggestions
- Guardrail flags are being triggered. Review the most common flags:
  - unknown_action: 155
  - blocked_action: 4
- Suggested:
  - For frequent `blocked_action` flags, check if users need safe alternatives.
  - For `risky_action` flags, ensure confirmation flows are clear in the UI.

## 3. Reliability Suggestions
- No workflow executions recorded. Run more end-to-end flows to gather data.