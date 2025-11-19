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
    get_logs
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
    cur.execute("SELECT user_id, role FROM users WHERE username=? AND password=?", 
                (username, password))
    user = cur.fetchone()
    conn.close()
    return user


# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Hospital System", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = None

st.title("Hospital Management System - Secure Dashboard")

if "app_start_time" not in st.session_state:
    st.session_state.app_start_time = datetime.now()

start_time_display = st.session_state.app_start_time.strftime("%Y-%m-%d %H:%M:%S")
current_time = datetime.now()
current_time_display = current_time.strftime("%Y-%m-%d %H:%M:%S")
uptime_duration = current_time - st.session_state.app_start_time
uptime_display = str(uptime_duration).split(".")[0]

st.info(
    f"App started: {start_time_display} | Current time: {current_time_display} | Uptime: {uptime_display}"
)


# ---------------------------
# LOGIN PAGE
# ---------------------------
if not st.session_state.logged_in:

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
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

    st.sidebar.title("Navigation")
    st.sidebar.write(f"Logged in as: **{st.session_state.role}**")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.role = None
        st.rerun()

    role = st.session_state.role



    # ======================================================
    # ===============  ADMIN DASHBOARD  =====================
    # ======================================================
    if role == "admin":

        st.header("Admin Dashboard")
        st.subheader("Patient Management (View / Add / Edit / Delete)")

        # LOAD PATIENTS
        patients = get_all_patients()

        # CSV export for admins
        csv_header = "patient_id,name,contact,diagnosis,anonymized_name,anonymized_contact,date_added"
        csv_rows = "\n".join(
            ",".join(str(value or "") for value in patient)
            for patient in patients
        )
        csv_data = csv_header + ("\n" + csv_rows if csv_rows else "")

        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="patients_export.csv"
        )

        st.write("### Patient Records")
        st.dataframe(
            [{
                "ID": p[0],
                "Name": p[1],
                "Contact": p[2],
                "Diagnosis": p[3],
                "Anon Name": p[4],
                "Anon Contact": p[5],
                "Date Added": p[6]
            } for p in patients],
            use_container_width=True
        )


        # -------------- ADD PATIENT --------------
        st.write("---")
        st.write("## Add New Patient")

        name = st.text_input("Patient Name")
        contact = st.text_input("Contact Number")
        diagnosis = st.text_input("Diagnosis")

        if st.button("Add Patient"):
            if name and contact and diagnosis:

                anon_name = mask_name(name)
                anon_contact = mask_contact(contact)

                add_patient(name, contact, diagnosis, anon_name, anon_contact)

                log_action(st.session_state.user_id, role, "add_patient",
                           f"Added patient {name}")

                st.success("Patient added successfully!")
                st.rerun()
            else:
                st.error("All fields are required!")


        # -------------- EDIT / DELETE PATIENT --------------
        st.write("---")
        st.write("## Edit / Delete Patient")

        patient_ids = [p[0] for p in patients]

        if patient_ids:
            selected_id = st.selectbox("Select Patient ID", patient_ids)

            selected = next((p for p in patients if p[0] == selected_id), None)

            if selected:
                new_name = st.text_input("Edit Name", selected[1])
                new_contact = st.text_input("Edit Contact", selected[2])
                new_diagnosis = st.text_input("Edit Diagnosis", selected[3])

                if st.button("Update Patient"):
                    update_patient(selected_id, new_name, new_contact, new_diagnosis)

                    log_action(st.session_state.user_id, role, "edit_patient",
                               f"Edited patient ID {selected_id}")

                    st.success("Patient updated successfully!")
                    st.rerun()

                if st.button("Delete Patient"):
                    delete_patient(selected_id)

                    log_action(st.session_state.user_id, role, "delete_patient",
                               f"Deleted patient ID {selected_id}")

                    st.error("Patient deleted.")
                    st.rerun()
        else:
            st.info("No patients available.")



        # -------------- AUDIT LOG VIEWER --------------
        st.write("---")
        st.subheader("Integrity Audit Log (Admin Only)")

        logs = get_logs()

        if not logs:
            st.info("No logs recorded yet.")
        else:
            log_rows = [{
                "Log ID": l[0],
                "User ID": l[1],
                "Role": l[2],
                "Action": l[3],
                "Timestamp": l[4],
                "Details": l[5],
            } for l in logs]

            st.dataframe(log_rows, use_container_width=True)

            st.write("### Filter Logs")

            role_filter = st.selectbox(
                "Filter by role:",
                ["All", "admin", "doctor", "receptionist"]
            )

            action_filter = st.text_input("Search action text (optional)").lower()

            filtered_logs = [
                l for l in logs
                if (role_filter == "All" or l[2] == role_filter) and
                   (action_filter in l[3].lower())
            ]

            st.write("### Filtered Results")

            flt_rows = [{
                "Log ID": l[0],
                "User ID": l[1],
                "Role": l[2],
                "Action": l[3],
                "Timestamp": l[4],
                "Details": l[5],
            } for l in filtered_logs]

            st.dataframe(flt_rows, use_container_width=True)




    # ======================================================
    # ===============  DOCTOR DASHBOARD  ====================
    # ======================================================
    elif role == "doctor":

        st.header("Doctor Dashboard")
        st.subheader("Anonymized Patient Roster")

        patients = get_all_patients()

        if not patients:
            st.info("No patients available.")
        else:

            diagnosis_options = ["All"] + sorted({p[3] for p in patients if p[3]})
            selected_diag = st.selectbox("Filter by diagnosis", diagnosis_options)

            search_term = st.text_input("Search by patient ID or anonymized contact").strip().lower()

            def matches(patient):
                if selected_diag != "All" and patient[3] != selected_diag:
                    return False
                if search_term:
                    return search_term in str(patient[0]).lower() or search_term in (patient[5] or "").lower()
                return True

            filtered = [p for p in patients if matches(p)]

            rows = [{
                "ID": p[0],
                "Anon Name": p[4],
                "Anon Contact": p[5],
                "Diagnosis": p[3],
                "Date Added": p[6]
            } for p in filtered]

            st.dataframe(rows, use_container_width=True)



    # ======================================================
    # ============  RECEPTIONIST DASHBOARD  ================
    # ======================================================
    elif role == "receptionist":

        st.header("Receptionist Dashboard")
        st.subheader("Add / Edit Patients (Sensitive Data Hidden)")

        patients = get_all_patients()

        st.write("### Patient Records (Restricted View)")
        st.dataframe(
            [{
                "ID": p[0],
                "Anonymized Name": p[4],
                "Anonymized Contact": p[5],
                "Date Added": p[6]
            } for p in patients],
            use_container_width=True
        )

        # ADD PATIENT
        st.write("---")
        st.write("## Add New Patient")

        name = st.text_input("Enter Patient Name (Real)")
        contact = st.text_input("Enter Contact Number (Real)")
        diagnosis = st.text_input("Enter Diagnosis (Real)")

        if st.button("Add Patient"):
            if name and contact and diagnosis:

                anon_name = mask_name(name)
                anon_contact = mask_contact(contact)

                add_patient(name, contact, diagnosis, anon_name, anon_contact)

                log_action(st.session_state.user_id, role, "add_patient",
                           f"Receptionist added: {anon_name}")

                st.success("Patient added successfully!")
                st.rerun()
            else:
                st.error("All fields are required!")

        # EDIT PATIENT
        st.write("---")
        st.write("## Edit Patient (Sensitive fields hidden)")

        patient_ids = [p[0] for p in patients]

        if patient_ids:
            selected_id = st.selectbox("Select Patient ID to Edit", patient_ids)

            selected = next((p for p in patients if p[0] == selected_id), None)

            if selected:
                st.info(f"Editing anonymized record: **{selected[4]}**")

                new_name = st.text_input("Edit Name (Real Value Hidden)")
                new_contact = st.text_input("Edit Contact (Real Value Hidden)")
                new_diagnosis = st.text_input("Edit Diagnosis (Real Value Hidden)")

                if st.button("Update Patient"):
                    if new_name and new_contact and new_diagnosis:
                        update_patient(selected_id, new_name, new_contact, new_diagnosis)

                        log_action(
                            st.session_state.user_id,
                            role,
                            "edit_patient",
                            f"Receptionist edited ID {selected_id}"
                        )

                        st.success("Patient updated successfully!")
                        st.rerun()
                    else:
                        st.error("All fields must be filled")
        else:
            st.info("No patients available to edit.")
