# Step 4 Day 2 — OpenAPI Notes

Endpoints:
1. GET /api/dashboard
   - Returns: DashboardResponse (Knowledge, Pattern, Skill KPIs)
   - Source mapping: ingestion logs, automation suggestions, feedback metrics

2. GET /api/journal
   - Returns: JournalResponse (entries with pagination)
   - Fields: id, timestamp, title, summary, tags, source, confidence, pinned
   - Future source: learning_journal table (planned Step 6)
