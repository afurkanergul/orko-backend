# 🧠 ORKO AI — Step 11 / Sub-Step 1 E : Performance Observation Summary  

**Date:** 2025-11-01  
**Engineer:** Ahmet Ergul  
**Environment:** Local PostgreSQL 18 (on 127.0.0.1)  

---

## 🔍 Objective  
Capture baseline query-performance data before optimization.  
This record provides the “before” snapshot for Step 11 → Sub-Step 2 (Add Indexes to Speed Up Queries).

---

## 🧩 Profiling Setup
| Parameter | Status |
|------------|---------|
| `log_min_duration_statement` | `200 ms` |
| `track_io_timing` | `on` |
| `pg_stat_statements` | installed & active |
| Test dataset | 20 000 rows in `logs` table |
| Tables observed | `logs`, `users` ( `trades` coming next ) |

---

## ⚙️ Representative Queries and Timing Results
| Query | Purpose | Avg Execution Time |
|--------|----------|--------------------|
| `SELECT * FROM logs ORDER BY created_at DESC LIMIT 5000;` | High-volume feed retrieval (sort bottleneck) | ≈ 548 ms |
| `SELECT COUNT(*) FROM logs WHERE org_id = 1;` | Org-scoped analytics (filter bottleneck) | ≈ 267 ms |

---

## 🧭 Findings
1. **Full-table scans** observed for `org_id` filters.  
2. **Costly sorts** on `created_at DESC`.  
3. IO and CPU usage increase proportionally with row count → classic sign of missing indexes.  
4. No critical locking or deadlocks detected during profiling.

---

## 🧱 Preliminary Optimization Targets
| Table | Columns to Index | Rationale |
|--------|------------------|------------|
| `logs` | `org_id` | Speed up frequent WHERE clauses in count & filter queries |
| `logs` | `created_at DESC` | Optimize sorting for timeline queries and recent logs |

---

## 🗂 Next Actions
- Proceed to **Sub-Step 2 (A–E)** to create and benchmark indexes.  
- Re-run the same queries post-indexing to record improvement in ms.  
- Append results to `db_optimization_results.md`.

---

✅ **Validation Checklist**
- [x] Performance logging enabled  
- [x] Representative queries measured  
- [x] Slow operations identified  
- [x] Index candidates documented  
- [x] File saved to `/backend/docs/`

---

**End of Sub-Step 1 E — Performance Observation Complete**  
Next: **Sub-Step 2 — Add Indexes to Speed Up Queries**
