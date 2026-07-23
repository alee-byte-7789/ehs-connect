# EHS Connect — Entity Relationship Diagram (Module 2)

This diagram reflects exactly what is implemented in `backend/app/models/`.
Rendered from the live SQLAlchemy models and verified against a real
migration (`alembic/versions/88ba86ceafae_initial_schema.py`) — not
hand-drawn from the spec.

```mermaid
erDiagram
    HOUSE ||--o{ RESIDENT : "has"
    HOUSE ||--o{ COMPLAINT : "has"
    RESIDENT ||--o{ COMPLAINT : "raises"
    RESIDENT ||--o{ FEEDBACK : "gives"
    RESIDENT ||--o{ APPLICATION_FEEDBACK : "gives"
    STAFF ||--o{ COMPLAINT : "assigned to"
    COMPLAINT ||--o{ COMPLAINT_HISTORY : "logs"
    COMPLAINT ||--o| FEEDBACK : "receives (optional, post-resolution)"

    HOUSE {
        int id PK
        string house_code UK "EHS-B-026"
        string block
        string address_meta
        datetime created_at
    }

    RESIDENT {
        int id PK
        string resident_code UK "EHS-B-026-O / -T1 (nullable until approved)"
        int house_id FK
        string full_name
        string phone
        string email
        string password_hash
        enum resident_type "owner | tenant"
        bool is_employee
        string employee_number
        string owner_house_number
        string owner_name
        string owner_cnic
        string owner_phone
        enum verification_status "pending | approved | rejected"
        int tenant_sequence
        datetime last_login
        datetime created_at
    }

    ADMIN {
        int id PK
        string full_name
        string email UK
        string password_hash
        enum role "housing_office | it_admin | super_admin"
        datetime created_at
    }

    STAFF {
        int id PK
        string full_name
        string phone
        enum category "electrician | plumber | mason | security | sanitation | other"
        bool is_active
        datetime created_at
    }

    COMPLAINT {
        int id PK
        string complaint_code UK
        int resident_id FK
        int house_id FK
        enum category "general | infrastructure | internal"
        string subcategory
        text description
        text photo_urls "JSON-encoded list"
        enum status "pending|accepted|assigned|in_progress|resolved|closed|reopened"
        int assigned_staff_id FK
        int close_count "guards: resident closes exactly once"
        datetime created_at
        datetime updated_at
        datetime closed_at
    }

    COMPLAINT_HISTORY {
        int id PK
        int complaint_id FK
        enum from_status
        enum to_status
        enum changed_by_type "resident | admin | staff | system"
        int changed_by_id
        text note
        datetime timestamp
    }

    FEEDBACK {
        int id PK
        int complaint_id FK, UK "1:1 with complaint"
        int resident_id FK
        int rating "CHECK 1<=rating<=5"
        text comment
        datetime created_at
    }

    APPLICATION_FEEDBACK {
        int id PK
        int resident_id FK
        enum type "feature_request | suggestion | bug_report"
        text message
        datetime created_at
    }

    EMERGENCY_CONTACT {
        int id PK
        string label
        string phone_number
        bool is_active
    }

    NOTIFICATION {
        int id PK
        enum recipient_type "resident | admin | staff"
        int recipient_id
        string title
        text body
        string type
        bool is_read
        datetime created_at
    }
```

## Notes on design decisions

- **`resident_code` is nullable.** A resident row exists from the moment of
  registration (status = `pending`), but the permanent code is only assigned
  by the server once a Housing Office Admin approves it — enforcing the
  "no self-assigned ID, no pre-verification access" rule from Section 6.3.
- **`Admin` and `Staff` are not connected to `Complaint` by history rows
  directly** — `ComplaintHistory.changed_by_id` is a plain integer paired
  with `changed_by_type`, not a foreign key to three different possible
  tables. This is a deliberate simplification (a polymorphic association)
  since SQLAlchemy has no clean native FK-to-multiple-tables construct; it
  is validated at the service layer instead.
- **`close_count` on `Complaint`**, not a separate table, because it's a
  single integer guard checked on every close attempt — no need for the
  overhead of a join.
- **`Feedback` is 1:1 with `Complaint`** via a `unique=True` FK plus
  `uselist=False` on the relationship, matching Section 6.2's "one
  complaint → one feedback" rule at the DB level, not just in application code.
