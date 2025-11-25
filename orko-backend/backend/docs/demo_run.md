# ORKO Step 6 Day 12 — Demo Script

## 1. Goal
Show full flow:
Natural-language command →
Parser →
Intent Mapper →
TriggerQueue →
WorkflowOrchestrator →
Simulate Mode Result

## 2. Setup
- FastAPI running
- Celery worker running
- Redis running
- Simulate = true for safe demonstration

## 3. Demo Commands (Multi-Industry)

### Trading
“Create a new wheat shipment contract to Egypt.”

### Logistics
“Book a truck for 500 MT barley to Ankara silo tomorrow.”

### Finance
“Generate a quarterly cashflow report.”

### HR
“Add a new employee in Dubai office to payroll.”

### IT Ops
“Restart the payments service in EU cluster.”

### Customer Support
“Show all open high-priority tickets for ACME Corp.”

### Operations
“Create a maintenance checklist for tomorrow.”

## 4. Expected Output
- JSON: domain/action/parameters
- `workflow_name` resolved by IntentMapper
- `trigger_job_id` returned from TriggerQueue
- `simulate = true` ensures safe execution

## 5. End State
- Parser logs captured
- Metrics unchanged (simulate mode)
- No destructive actions performed
