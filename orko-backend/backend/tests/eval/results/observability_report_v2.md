# ORKO Observability Dashboard v2

## 1. Traffic Overview
- Parser events: **306**
- Trigger events: **6**
- Workflow events: **0**

### Domain Traffic
- logistics: 53
- general: 225
- trading: 10
- docs: 18

### Action Frequency
- generate: 34
- restart: 4
- create: 47
- list: 40
- book: 4
- add: 6
- show: 27
- open: 3
- allocate: 3
- schedule: 15
- deploy: 6
- update: 3
- prepare: 6
- run: 6
- promote: 3
- rotate: 3
- rollback: 3
- increase: 3
- escalate: 3
- forecast: 9
- analyze: 9
- rebuild: 3
- classify: 3
- summarize: 15
- approve: 3
- draft: 12
- review: 6
- check: 3
- initiate: 3
- assign: 3
- optimize: 6
- inspect: 3
- tag: 3
- plan: 3
- record: 3

## 2. Latency (Workflow Execution)
- p50: 0.00 ms
- p95: 0.00 ms
- p99: 0.00 ms
- avg: 0.00 ms
- max: 0.00 ms

## 3. Errors
- Workflow errors: **0**

## 4. Guardrail Flags (Safety Usage)
- unknown_action: 155
- blocked_action: 4

## 5. Weak Domains (from Evaluator v2)
- marketing (F1=0.00, P=0.00, R=0.00)
- general (F1=0.00, P=0.00, R=0.00)
- general_admin (F1=0.00, P=0.00, R=0.00)
- knowledge_work (F1=0.00, P=0.00, R=0.00)
- operations (F1=0.00, P=0.00, R=0.00)
- logistics (F1=0.27, P=0.18, R=0.60)
- sales (F1=0.00, P=0.00, R=0.00)
- customer_support (F1=0.00, P=0.00, R=0.00)
- trading (F1=0.25, P=0.33, R=0.20)
- hr (F1=0.00, P=0.00, R=0.00)
- retail (F1=0.00, P=0.00, R=0.00)
- legal (F1=0.00, P=0.00, R=0.00)
- finance (F1=0.00, P=0.00, R=0.00)
- devops (F1=0.00, P=0.00, R=0.00)
- it_ops (F1=0.00, P=0.00, R=0.00)
- procurement (F1=0.00, P=0.00, R=0.00)
- manufacturing (F1=0.00, P=0.00, R=0.00)
- docs (F1=0.00, P=0.00, R=0.00)
- healthcare_admin (F1=0.00, P=0.00, R=0.00)
- energy (F1=0.00, P=0.00, R=0.00)
- analytics (F1=0.00, P=0.00, R=0.00)

## 6. Per-Domain PRF
### marketing
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=4
### general
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=74, FN=0
### general_admin
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=5
### knowledge_work
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=3
### operations
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=6
### logistics
- Accuracy: 0.00
- Precision: 0.18
- Recall: 0.60
- F1: 0.27
- TP=3, FP=14, FN=2
### sales
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=4
### customer_support
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=5
### trading
- Accuracy: 0.00
- Precision: 0.33
- Recall: 0.20
- F1: 0.25
- TP=1, FP=2, FN=4
### hr
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=5
### retail
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=6
### legal
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=7
### finance
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=6
### devops
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=5
### it_ops
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=7
### procurement
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=6
### manufacturing
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=7
### docs
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=6, FN=0
### healthcare_admin
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=3
### energy
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=6
### analytics
- Accuracy: 0.00
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- TP=0, FP=0, FN=5