sss### 1. Project Summary

- **Goal:** Build a mini hospital dashboard that respects the CIA triad (Confidentiality, Integrity, Availability) and GDPR-style best practices.
- **Tech Stack:** Streamlit + Python 3.11 + SQLite.
- **Key Files:**
  - `main.py` — Streamlit UI (login, dashboards, audit log, CSV export).
  - `database.py` — SQLite schema + helper functions.
  - `Assignment4.py` — text walkthrough of the CIA features (requested deliverable).
  - `hospital.db` — created automatically; stores users, patients, logs.

---

### 2. Getting Started

```bash
pip install streamlit
streamlit run main.py
```

Default users (inserted automatically):

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| Admin | `admin` | `admin123` | Full view (raw + anonymized), CRUD, audit logs, CSV export |
| Doctor | `DrBob` | `doc123` | View anonymized patient data only |
| Receptionist | `AliceRecep` | `rec123` | Add/Edit patients, sees anonymized identifiers |

---

### 3. CIA Breakdown (talking points)

**Confidentiality**
1. RBAC determines which dashboard appears after login.
2. `mask_name` and `mask_contact` produce ANON_/XXX-XXX-#### values.
3. Doctor view hides raw names/contact. Receptionist forms only show masked identifiers when editing.

**Integrity**
1. `log_action` records each login/add/edit/delete with timestamps.
2. Admin dashboard displays the “Integrity Audit Log” table plus filters (by role + keyword).
3. Form validation ensures users can’t submit blank patient data.

**Availability**
1. Uptime banner (top of the dashboard) shows start time and total uptime.
2. CSV export button gives admins a quick backup of all patient records.
3. `create_tables()` runs on startup so the database schema is ready even on a fresh clone.

Use this section when writing the report or presenting in class.

---

### 4. Demo / Screenshot Checklist

1. **Login screen** — show RBAC and credential input.
2. **Admin dashboard** — highlight raw + anonymized table, add/edit/delete, CSV button, audit log.
3. **Doctor dashboard** — show anonymized roster and filters.
4. **Receptionist dashboard** — explain how they add/edit patients without viewing raw identifiers.
5. **Assignment4.py** — run `python Assignment4.py` to print the textual walkthrough (nice addition to the PDF appendix).


### 5. Need to explain it live?

Use this script:
1. “We log in using seeded accounts; RBAC decides which view you see.”
2. “Admins can see raw data and exported CSV; doctors only get anonymized info; receptionists add/edit from masked identifiers.”
3. “Every action is logged, and admins review the audit trail.”
4. “Uptime + CSV + SQLite ensure availability.”
5. “Assignment4.py provides the textual walkthrough for the professor.”


