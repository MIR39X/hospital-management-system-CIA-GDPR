import streamlit as st
from datetime import datetime
from database import (
    get_connection,
    create_tables,
    log_action,
    add_patient,
    get_all_patients,
    update_patient,
    delete_patient,
    get_logs,
)

# Initialize DB
create_tables()

# ---------------------------
# Anonymization Functions
# ---------------------------
def mask_name(name):
    return "ANON_" + str(abs(hash(name)) % 10000)


def mask_contact(contact):
    return "XXX-XXX-" + contact[-4:]


# ---------------------------
# Authentication
# ---------------------------
def authenticate_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, role FROM users WHERE username=? AND password=?",
        (username, password),
    )
    user = cur.fetchone()
    conn.close()
    return user


def render_kpi(label, value, badge=None):
    """Glassmorphism metric cards for repeated UI elements."""
    value_text = str(value)
    badge_html = f'<span class="kpi-badge">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="glass-card kpi-card">
            <p class="kpi-label">{label}</p>
            <h3 class="kpi-value">{value_text}</h3>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="PulseWatch Control Center", layout="wide")

CUSTOM_CSS = """
<style>
:root {
    --bg-dark: #020b1f;
    --bg-glass: rgba(8, 18, 43, 0.75);
    --accent: #48d6ff;
    --accent-strong: #f9a826;
    --text-muted: #8ba3c7;
}
[data-testid="stAppViewContainer"] > .main {
    background: radial-gradient(circle at top, rgba(44, 184, 251, 0.08), transparent 45%),
                radial-gradient(circle at 20% 20%, rgba(249, 168, 38, 0.08), transparent 25%),
                linear-gradient(135deg, #040c27, #071331 55%, #051226);
    color: #f2f6ff;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
.hero-card {
    background: linear-gradient(120deg, rgba(27, 53, 95, 0.8), rgba(12, 27, 58, 0.8));
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 30px;
    padding: 2.25rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 25px 80px rgba(0, 0, 0, 0.45);
}
.hero-card h1 {
    margin-bottom: 0.4rem;
}
.hero-card .eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.25em;
    font-size: 0.75rem;
    color: var(--accent);
}
.glass-card {
    background: var(--bg-glass);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}
.kpi-card {
    min-height: 120px;
}
.kpi-label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-muted);
    margin: 0 0 0.3rem 0;
}
.kpi-value {
    margin: 0;
    font-size: 2rem;
    color: #f9fbff;
}
.kpi-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.8rem;
    background: rgba(72, 214, 255, 0.12);
    color: var(--accent);
    border-radius: 999px;
    padding: 0.2rem 0.75rem;
}
[data-testid="stSidebar"] {
    background: rgba(1, 4, 18, 0.75);
    backdrop-filter: blur(14px);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}
[data-testid="stSidebar"] * {
    color: #e3ecff !important;
}
.stButton>button {
    width: 100%;
    background: linear-gradient(120deg, #4f46e5, #18b4ff);
    color: white;
    border-radius: 999px;
    border: none;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    transition: all 0.2s ease;
}
.stButton>button:hover {
    box-shadow: 0 12px 30px rgba(24, 180, 255, 0.35);
    transform: translateY(-1px);
}
.stTextInput>div>div>input,
.stSelectbox>div>div>div>input,
.stTextArea>div>textarea {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 14px;
    color: #fdfdff;
}
.stSelectbox>div>div>div {
    color: #fdfdff;
}
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, 0.03);
    padding: 0.3rem;
    border-radius: 999px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 999px;
    padding: 0.35rem 1.5rem;
    color: var(--text-muted);
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(120deg, #4f46e5, #18b4ff);
    color: white;
}
[data-testid="stDataFrame"] {
    background: rgba(1, 8, 30, 0.55);
    border-radius: 20px;
    padding: 0.5rem;
}
.tip-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.tip-card ul {
    padding-left: 1.2rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = None

st.markdown(
    """
    <div class="hero-card">
        <p class="eyebrow">PulseWatch Security Stack</p>
        <h1>23K2085 - Arsalan Mir</h1>
        <p><strong>Information Security Course</strong></p>
        <p>Hardest assignment I have ever done so far.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "app_start_time" not in st.session_state:
    st.session_state.app_start_time = datetime.now()

start_time_display = st.session_state.app_start_time.strftime("%Y-%m-%d %H:%M:%S")
current_time = datetime.now()
current_time_display = current_time.strftime("%Y-%m-%d %H:%M:%S")
uptime_duration = current_time - st.session_state.app_start_time
uptime_display = str(uptime_duration).split(".")[0]

status_cols = st.columns(3)
with status_cols[0]:
    render_kpi("Session Start", start_time_display, "Application boot")
with status_cols[1]:
    render_kpi("Current Time", current_time_display, "Local server clock")
with status_cols[2]:
    render_kpi("Uptime", uptime_display, "Live monitoring")


# ---------------------------
# LOGIN PAGE
# ---------------------------
if not st.session_state.logged_in:

    st.markdown("### Encrypted Gateway")
    st.markdown("#### Authenticate to continue")
    username = st.text_input("Username", placeholder="admin@pulsewatch")
    password = st.text_input("Password", type="password", placeholder="********")

    if st.button("Authenticate Session", use_container_width=True):
        user = authenticate_user(username, password)

        if user:
            st.success("Login successful!")
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.role = user[1]

            log_action(user[0], user[1], "login", f"{username} logged in")

            st.rerun()
        else:
            st.error("Invalid username or password")


# ---------------------------
# MAIN DASHBOARD (After Login)
# ---------------------------
else:

    st.sidebar.markdown("## Quick Navigation")
    st.sidebar.caption("Role-aware controls with zero-trust logout.")
    st.sidebar.markdown(f"**User ID:** `{st.session_state.user_id}`")
    st.sidebar.markdown(f"**Role:** {st.session_state.role.title()}")

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.role = None
        st.rerun()

    role = st.session_state.role

    # ======================================================
    # ===============  ADMIN DASHBOARD  =====================
    # ======================================================
    if role == "admin":

        st.markdown("### Admin Command Deck")
        patients = get_all_patients()

        total_patients = len(patients)
        unique_diagnoses = len({p[3] for p in patients if p[3]})
        last_entry = patients[-1][6] if patients else "Awaiting first entry"

        metric_cols = st.columns(3)
        with metric_cols[0]:
            render_kpi("Patients Indexed", total_patients, "Active records")
        with metric_cols[1]:
            render_kpi("Unique Diagnoses", unique_diagnoses, "Diversity snapshot")
        with metric_cols[2]:
            render_kpi("Last Entry", last_entry, "Most recent record")

        overview_tab, manage_tab, audit_tab = st.tabs(
            ["Patient Intelligence", "Manage Patients", "Audit Trail"]
        )

        with overview_tab:
            st.markdown("#### Patient intelligence stream")
            st.caption("Export roster data with both sensitive and anonymized identifiers.")

            csv_header = (
                "patient_id,name,contact,diagnosis,anonymized_name,anonymized_contact,date_added"
            )
            csv_rows = "\n".join(
                ",".join(str(value or "") for value in patient)
                for patient in patients
            )
            csv_data = csv_header + ("\n" + csv_rows if csv_rows else "")

            st.download_button(
                label="Download roster CSV",
                data=csv_data,
                file_name="patients_export.csv",
            )

            st.dataframe(
                [
                    {
                        "ID": p[0],
                        "Name": p[1],
                        "Contact": p[2],
                        "Diagnosis": p[3],
                        "Anon Name": p[4],
                        "Anon Contact": p[5],
                        "Date Added": p[6],
                    }
                    for p in patients
                ],
                use_container_width=True,
            )

        with manage_tab:
            st.markdown("#### Secure record maintenance")
            add_col, edit_col = st.columns(2)

            with add_col:
                st.markdown("##### Add new patient")
                name = st.text_input("Patient Name", key="admin_add_name", placeholder="Jane Doe")
                contact = st.text_input(
                    "Contact Number", key="admin_add_contact", placeholder="555-0102"
                )
                diagnosis = st.text_input(
                    "Diagnosis", key="admin_add_diagnosis", placeholder="Hypertension"
                )

                if st.button("Add Patient", key="admin_add_btn", use_container_width=True):
                    if name and contact and diagnosis:

                        anon_name = mask_name(name)
                        anon_contact = mask_contact(contact)

                        add_patient(name, contact, diagnosis, anon_name, anon_contact)

                        log_action(
                            st.session_state.user_id,
                            role,
                            "add_patient",
                            f"Added patient {name}",
                        )

                        st.success("Patient added successfully!")
                        st.rerun()
                    else:
                        st.error("All fields are required!")

            with edit_col:
                st.markdown("##### Update or delete patient")
                patient_ids = [p[0] for p in patients]

                if patient_ids:
                    selected_id = st.selectbox(
                        "Select Patient ID", patient_ids, key="admin_edit_select"
                    )

                    selected = next((p for p in patients if p[0] == selected_id), None)

                    if selected:
                        new_name = st.text_input(
                            "Edit Name", value=selected[1], key="admin_edit_name"
                        )
                        new_contact = st.text_input(
                            "Edit Contact", value=selected[2], key="admin_edit_contact"
                        )
                        new_diagnosis = st.text_input(
                            "Edit Diagnosis", value=selected[3], key="admin_edit_diagnosis"
                        )

                        if st.button(
                            "Update Patient", key="admin_update_btn", use_container_width=True
                        ):
                            update_patient(selected_id, new_name, new_contact, new_diagnosis)

                            log_action(
                                st.session_state.user_id,
                                role,
                                "edit_patient",
                                f"Edited patient ID {selected_id}",
                            )

                            st.success("Patient updated successfully!")
                            st.rerun()

                        if st.button(
                            "Delete Patient", key="admin_delete_btn", use_container_width=True
                        ):
                            delete_patient(selected_id)

                            log_action(
                                st.session_state.user_id,
                                role,
                                "delete_patient",
                                f"Deleted patient ID {selected_id}",
                            )

                            st.error("Patient deleted.")
                            st.rerun()
                else:
                    st.info("No patients available.")

        with audit_tab:
            st.markdown("#### Integrity audit trail")
            logs = get_logs()

            if not logs:
                st.info("No logs recorded yet.")
            else:
                log_rows = [
                    {
                        "Log ID": l[0],
                        "User ID": l[1],
                        "Role": l[2],
                        "Action": l[3],
                        "Timestamp": l[4],
                        "Details": l[5],
                    }
                    for l in logs
                ]

                st.dataframe(log_rows, use_container_width=True)

                st.markdown("##### Filter logs")
                filter_cols = st.columns(2)

                with filter_cols[0]:
                    role_filter = st.selectbox(
                        "Filter by role", ["All", "admin", "doctor", "receptionist"],
                        key="audit_role_filter",
                    )
                with filter_cols[1]:
                    action_filter = st.text_input(
                        "Search action text (optional)", key="audit_action_filter"
                    ).lower()

                filtered_logs = [
                    l
                    for l in logs
                    if (role_filter == "All" or l[2] == role_filter)
                    and action_filter in l[3].lower()
                ]

                flt_rows = [
                    {
                        "Log ID": l[0],
                        "User ID": l[1],
                        "Role": l[2],
                        "Action": l[3],
                        "Timestamp": l[4],
                        "Details": l[5],
                    }
                    for l in filtered_logs
                ]

                st.dataframe(flt_rows, use_container_width=True)

    # ======================================================
    # ===============  DOCTOR DASHBOARD  ====================
    # ======================================================
    elif role == "doctor":

        st.markdown("### Doctor Operations Board")
        patients = get_all_patients()

        diag_count = len({p[3] for p in patients if p[3]})
        doc_cols = st.columns(2)
        with doc_cols[0]:
            render_kpi("Roster Size", len(patients), "Anonymized view")
        with doc_cols[1]:
            render_kpi("Unique Diagnoses", diag_count, "Clinical spread")

        if not patients:
            st.info("No patients available.")
        else:
            filter_cols = st.columns(2)

            diagnosis_options = ["All"] + sorted({p[3] for p in patients if p[3]})
            with filter_cols[0]:
                selected_diag = st.selectbox(
                    "Filter by diagnosis", diagnosis_options, key="doctor_diagnosis_filter"
                )

            with filter_cols[1]:
                search_term = st.text_input(
                    "Search by patient ID or anonymized contact",
                    key="doctor_search",
                ).strip().lower()

            def matches(patient):
                if selected_diag != "All" and patient[3] != selected_diag:
                    return False
                if search_term:
                    return search_term in str(patient[0]).lower() or search_term in (patient[5] or "").lower()
                return True

            filtered = [p for p in patients if matches(p)]

            rows = [
                {
                    "ID": p[0],
                    "Anon Name": p[4],
                    "Anon Contact": p[5],
                    "Diagnosis": p[3],
                    "Date Added": p[6],
                }
                for p in filtered
            ]

            st.dataframe(rows, use_container_width=True)

    # ======================================================
    # ============  RECEPTIONIST DASHBOARD  ================
    # ======================================================
    elif role == "receptionist":

        st.markdown("### Reception Operations Center")
        patients = get_all_patients()

        roster_tab, manage_tab = st.tabs(["Restricted Roster", "Manage Patients"])

        with roster_tab:
            st.caption("All identifiers remain anonymized in this view.")
            st.dataframe(
                [
                    {
                        "ID": p[0],
                        "Anonymized Name": p[4],
                        "Anonymized Contact": p[5],
                        "Date Added": p[6],
                    }
                    for p in patients
                ],
                use_container_width=True,
            )

        with manage_tab:
            st.markdown("#### Add or edit patients")
            rec_cols = st.columns(2)

            with rec_cols[0]:
                st.markdown("##### Add new patient")
                name = st.text_input("Enter Patient Name (Real)", key="rec_add_name")
                contact = st.text_input(
                    "Enter Contact Number (Real)", key="rec_add_contact"
                )
                diagnosis = st.text_input("Enter Diagnosis (Real)", key="rec_add_diagnosis")

                if st.button("Add Patient", key="rec_add_btn", use_container_width=True):
                    if name and contact and diagnosis:

                        anon_name = mask_name(name)
                        anon_contact = mask_contact(contact)

                        add_patient(name, contact, diagnosis, anon_name, anon_contact)

                        log_action(
                            st.session_state.user_id,
                            role,
                            "add_patient",
                            f"Receptionist added: {anon_name}",
                        )

                        st.success("Patient added successfully!")
                        st.rerun()
                    else:
                        st.error("All fields are required!")

            with rec_cols[1]:
                st.markdown("##### Edit patient")
                patient_ids = [p[0] for p in patients]

                if patient_ids:
                    selected_id = st.selectbox(
                        "Select Patient ID to Edit", patient_ids, key="rec_edit_select"
                    )

                    selected = next((p for p in patients if p[0] == selected_id), None)

                    if selected:
                        st.info(f"Editing anonymized record: **{selected[4]}**")

                        new_name = st.text_input(
                            "Edit Name (Real Value Hidden)", key="rec_edit_name"
                        )
                        new_contact = st.text_input(
                            "Edit Contact (Real Value Hidden)", key="rec_edit_contact"
                        )
                        new_diagnosis = st.text_input(
                            "Edit Diagnosis (Real Value Hidden)", key="rec_edit_diagnosis"
                        )

                        if st.button(
                            "Update Patient", key="rec_update_btn", use_container_width=True
                        ):
                            if new_name and new_contact and new_diagnosis:
                                update_patient(selected_id, new_name, new_contact, new_diagnosis)

                                log_action(
                                    st.session_state.user_id,
                                    role,
                                    "edit_patient",
                                    f"Receptionist edited ID {selected_id}",
                                )

                                st.success("Patient updated successfully!")
                                st.rerun()
                            else:
                                st.error("All fields must be filled")
                else:
                    st.info("No patients available to edit.")
