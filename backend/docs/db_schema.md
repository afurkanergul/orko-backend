# 🧠 ORKO AI Database Schema
*(Documented on November 1, 2025)*  

This document describes the **structure and purpose** of the ORKO AI database.  
It summarizes how the system’s main tables store information and how they relate to one another.  
The goal is to help anyone — developer, analyst, or AI agent — quickly understand the data model.

---
## 🧍‍♂️ users  
Stores all individuals registered in ORKO (admins, operators, viewers).

**Key Columns:**  
- `id` – Primary Key (unique user ID)  
- `org_id` – Foreign Key → `orgs.id`  
- `name`, `email`, `hashed_password`, `role`, `status`  
- `created_at`, `updated_at`

**Purpose:**  
Tracks every user and their role within an organization.

---

## 🏢 orgs  
Represents companies or workspaces using ORKO.

**Key Columns:**  
- `id` – Primary Key  
- `name`, `domain`, `plan`, `status`  
- `created_at`, `updated_at`

**Relations:**  
- One org → many users (`users.org_id`)  
- One org → many logs (`logs.org_id`)

**Purpose:**  
Defines each customer organization and its subscription plan.

---

## 🔐 auth_tokens  
Manages login sessions and API authentication tokens.

**Key Columns:**  
- `id` – Primary Key  
- `user_id` – FK → `users.id`  
- `token_hash`, `expires_at`, `revoked_at`, `status`  
- `created_at`, `updated_at`

**Purpose:**  
Tracks secure logins and token lifecycles.

---

## ⚙️ automations  
Contains user-created automation rules.

**Key Columns:**  
- `id` – Primary Key  
- `user_id` – FK → `users.id`  
- `name`, `trigger`, `action`, `config`, `last_run_at`, `status`  
- `created_at`, `updated_at`

**Purpose:**  
Stores AI-driven automations that streamline workflows.

---

## 🧾 logs  
Captures user and system activity.

**Key Columns:**  
- `id` – Primary Key  
- `org_id` – FK → `orgs.id`  
- `user_id` – FK → `users.id`  
- `level`, `event`, `details`, `created_at`

**Purpose:**  
Records events for analytics, audit, and debugging.

---

## 💬 feedback  
Stores user feedback and ratings.

**Key Columns:**  
- `id` – Primary Key  
- `user_id` – FK → `users.id`  
- `rating`, `comment`, `context`, `created_at`, `updated_at`

**Purpose:**  
Captures user sentiment and improvement suggestions.
---

## 🖼️ Entity Relationship Diagram (ERD)

Below is the visual map of ORKO’s database structure.  
Each box represents a table, and lines show foreign key links (relationships).

![ORKO Database ERD](./orko_db_2025_11_01.png)

*Legend:*  
🔑 Primary Key  🔗 Foreign Key  🧩 Relationship between tables

---

## 🧩 Glossary

| Term | Meaning |
|------|----------|
| **PK** | Primary Key — unique identifier for each record in a table |
| **FK** | Foreign Key — a column that links to another table’s primary key |
| **Org** | Organization using ORKO |
| **User** | Account that belongs to an organization |
| **Automation** | AI-driven workflow rule created by a user |
| **Feedback** | Comment or rating submitted by a user |
| **Token** | Secure login or API session identifier |
| **Log** | Recorded event or system action |
| **Status** | Field showing active/suspended/archived state |
| **Timestamps** | `created_at` and `updated_at` fields for auditing and history |
