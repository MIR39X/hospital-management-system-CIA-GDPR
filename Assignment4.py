"""
Assignment4.py
---------------
This companion script documents the major steps and controls implemented in the
DPR-compliant mini Hospital Management System. It serves as the "Assignment4"
artifact requested in the brief (alternative to a Jupyter notebook) and can be
executed as a standalone walkthrough of the CIA (Confidentiality, Integrity,
Availability) features wired into the Streamlit dashboard and SQLite backend.

Running this file provides a narrated checklist so the instructor can verify the
system behaviour without digging through the Streamlit code.
"""

from textwrap import dedent

from database import (
    create_tables,
    get_connection,
    get_all_patients,
    get_logs,
)


def print_section(title: str, body: str) -> None:
    """Utility to print clearly separated sections."""
    line = "=" * len(title)
    print(f"\n{title}\n{line}")
    print(dedent(body).strip())


def confidentiality_steps() -> None:
    """List confidentiality controls implemented in main.py/database.py."""
    body = """
    1. Role-Based Access Control (RBAC):
       - Credentials stored in the `users` table (admin/doctor/receptionist).
       - `authenticate_user` assigns a role which controls the Streamlit UI.

    2. Data masking/anonymization:
       - Functions `mask_name` and `mask_contact` generate ANON_* and XXX-XXX-#### values.
       - Admin sees both raw + masked data. Doctor sees anonymized-only views.
       - Receptionist only interacts with anonymized identifiers and never sees decrypted
         values in the UI.

    3. Session security:
       - Streamlit `st.session_state` keeps track of `logged_in`, `user_id`, and `role`.

    4. Database access:
       - All CRUD operations flow through `database.py`, ensuring a single enforcement point.
    """
    print_section("CONFIDENTIALITY CONTROLS", body)


def integrity_steps() -> None:
    """List integrity-oriented features."""
    body = """
    1. Audit logging (`log_action`):
       - Every login, add, edit, delete, and receptionist view is logged with
         user_id, role, timestamp, and action details.

    2. Database schema:
       - Patients/logs tables enforce primary keys and prevent orphaned references.

    3. Streamlit Admin Audit Dashboard:
       - Admin-only view (`Integrity Audit Log`) surfaces all log entries and
         provides filters by role and keyword.

    4. Input validation:
       - The UI requires all patient fields before add/update buttons succeed.
    """
    print_section("INTEGRITY CONTROLS", body)


def availability_steps() -> None:
    """List availability features."""
    body = """
    1. System uptime widget:
       - `main.py` tracks `st.session_state["app_start_time"]` and displays
         the uptime/current time banner on every page.

    2. CSV Export:
       - Admin can download full patient data via `st.download_button`, providing
         a fast backup for recovery.

    3. Stable SQLite backend:
       - `database.py` centralizes all queries; `create_tables()` is called at startup.

    4. Simple exception boundaries:
       - While Streamlit handles UI failures gracefully, the database helper functions
         close connections reliably on each call to avoid locking.
    """
    print_section("AVAILABILITY CONTROLS", body)


def db_snapshot() -> None:
    """
    Provide a quick database snapshot to demonstrate the script actually touches
    the live SQLite file used by the dashboard.
    """
    create_tables()
    patients = get_all_patients()
    logs = get_logs()

    print_section(
        "DATABASE SNAPSHOT",
        f"""
        Total Patients : {len(patients)}
        Total Log Rows : {len(logs)}

        Hint:
          • Populate the `patients` table via the Streamlit admin/receptionist UI.
          • Review the `logs` table via the Audit Log viewer.

        Use `hospital.db` with any SQLite client for deeper inspection.
        """,
    )



def main() -> None:
    """Entry point for CLI walkthrough."""
    print_section("ASSIGNMENT 4 WALKTHROUGH", "CIA-oriented implementation summary.")
    confidentiality_steps()
    integrity_steps()
    availability_steps()
    db_snapshot()


if __name__ == "__main__":
    main()
