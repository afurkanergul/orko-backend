# Step 2 — Day 7 — RBAC Prep Notes (Sub-Step 1)

## 🎯 Goal
Plan the multi-tenant "organization bubble" before changing any tables.

---

## 💡 Key Idea
- Every record we care about will have a sticker/tag called `org_id`.
- Users only see rows with their own `org_id`.

---

## 🗂️ Core Tables That Will Be Tagged with `org_id` (list to confirm)
- users → ✅ YES
- trades → ✅ YES
- files → ✅ YES
- (optional later) messages, tasks, invoices, audit_logs, etc.

---

## 🧱 Org ID Type Decision
- Use **INTEGER** for org_id (simple, fast).
- We'll add **foreign keys** later if/when we add an organizations table.

**Decision:** `org_id = INTEGER` *(no FK on Day 7)*.  
FK can be added on **Day 8–9** if we introduce an `organizations` table.

---

## 🔍 Default Visibility Rule (Mental Model)
> “When querying any multi-tenant table, always add  
> `WHERE org_id = :current_user_org_id`”

This rule ensures each user only sees data from their own organization.

---

## 📦 Minimum Day 7 Deliverables
- Add `org_id` to `users`, `trades`, `files`
- Create `roles`, `permissions`, `user_roles` tables
- Create ENUM `user_role` (`admin`, `operator`, `viewer`)
- Prove filtering by `org_id` works

---

## 🚫 What We Will NOT Do in Day 7
- ❌ No backend middleware yet  
- ❌ No API changes yet  
- ❌ No Alembic migrations yet (that’s Day 8)

---

## ✅ Table Checklist (tick as you go)

| Table Name | Action | Status |
|-------------|---------|--------|
| users | Add `org_id` (INTEGER) and `role` (ENUM) | [ ] |
| trades | Add `org_id` (INTEGER) | [ ] |
| files | Add `org_id` (INTEGER) | [ ] |
| roles | Create new table | [ ] |
| permissions | Create new table | [ ] |
| user_roles | Create new table | [ ] |
| Validation | Test `SELECT * FROM trades WHERE org_id = 1` returns only my org’s data | [ ] |

---

## 🧩 Query Copy Block (for reuse later)

```sql
-- Example read:
SELECT * FROM trades WHERE org_id = :org_id;

-- Example count:
SELECT COUNT(*) FROM files WHERE org_id = :org_id;

-- Example join (pattern):
SELECT t.*
FROM trades t
JOIN users u ON u.id = t.created_by
WHERE t.org_id = :org_id AND u.org_id = :org_id;

---

## 🪜 Part E — Understanding and Using the Filtering Rule

### Step 1 — What it means
Every time ORKO fetches data, it must filter by organization.  
The sentence  

```sql
WHERE org_id = :current_user_org_id

---

## ✅ Part G — Quick Self-Check

Before proceeding to Sub-Step 2 (adding org_id columns in pgAdmin), verify that:

| Checkpoint | Description | Done |
|-------------|--------------|------|
| 🎯 Goal & Key Idea | The purpose of RBAC and multi-tenant “bubble” is clearly described. | [x] |
| 🧱 Org ID Decision | `org_id = INTEGER` noted, FK deferred to Day 8–9. | [x] |
| 📋 Table Checklist | List of tables to update or create is present. | [x] |
| 💾 Query Copy Block | SQL examples for filtering by org_id included and closed properly. | [x] |
| 🪜 Part E | Filtering rule (steps 1–5 + summary) fully written. | [x] |
| 🧹 Formatting | All code blocks closed with ``` and file saved. | [x] |
| 🧠 Ready for Day 8 | pgAdmin installed and accessible; database connection tested. | [ ] |

> ✅ If every box except the last is checked, you are ready to start **Sub-Step 2: Add org_id columns**.
