## DPR-Compliant Mini Hospital Management System

Streamlit-based dashboard built for Assignment 4 (Information Security) to demonstrate the CIA triad (Confidentiality, Integrity, and Availability) while managing community hospital records.

---

### Project Overview

- **Frameworks:** Streamlit, Python 3.11, SQLite
- **Key Files**
  - `main.py` - Streamlit dashboard (login, RBAC, patient CRUD, audit viewer)
  - `database.py` - SQLite schema + DB helper functions
  - `Assignment4.py` - CIA walkthrough script requested by the assignment brief
  - `hospital.db` - SQLite database (auto-created)

---

### Setup & Run

```bash
pip install streamlit
streamlit run main.py
```

Default credentials (seeded automatically):

| Role | Username | Password | Access |
| --- | --- | --- | --- |
| Admin | `admin` | `admin123` | Full patient data + audit log, CSV export |
| Doctor | `DrBob` | `doc123` | Anonymized patient roster |
| Receptionist | `AliceRecep` | `rec123` | Add/Edit forms with anonymized identifiers |

---

### CIA Highlights

- **Confidentiality**
  - Role-based workflow (admin/doctor/receptionist)
  - `mask_name`/`mask_contact` anonymize PII columns
  - Receptionist UI never displays raw data

- **Integrity**
  - `log_action` records login + CRUD events with timestamps
  - Admin dashboard exposes an "Integrity Audit Log" with filters
  - Required field validation before add/edit actions

- **Availability**
  - Session uptime banner near the top of the dashboard
  - CSV export for admin backups
  - Simple, single-file SQLite backend with schema auto-creation

For a CLI-friendly summary, run:

```bash
python Assignment4.py
```

This prints the steps, CIA coverage, and DB snapshot (patient/log counts).

---

