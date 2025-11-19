import sqlite3
from datetime import datetime
DB_NAME = "hospital.db"

def get_connection():
    """Create a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # --- USERS TABLE ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
    """)

    # --- PATIENTS TABLE ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            diagnosis TEXT,
            anonymized_name TEXT,
            anonymized_contact TEXT,
            date_added TEXT
        );
    """)

    # --- LOGS TABLE ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            action TEXT,
            timestamp TEXT,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
    """)

    conn.commit()
    conn.close()
    insert_default_users()


def insert_default_users():
    """Inserts Admin, Doctor, Receptionist if not already present."""
    conn = get_connection()
    cur = conn.cursor()

    default_users = [
        ("admin", "admin123", "admin"),
        ("DrBob", "doc123", "doctor"),
        ("AliceRecep", "rec123", "receptionist")
    ]

    for username, pwd, role in default_users:
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, pwd, role)
            )

    conn.commit()
    conn.close()


def log_action(user_id, role, action, details=""):
    """Insert an action log entry into logs table."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO logs (user_id, role, action, timestamp, details)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, role, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), details))

    conn.commit()
    conn.close()


# ---------------------------
# PATIENT CRUD FUNCTIONS
# ---------------------------

def add_patient(name, contact, diagnosis, anonymized_name, anonymized_contact):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patients (name, contact, diagnosis, anonymized_name, anonymized_contact, date_added)
        VALUES (?, ?, ?, ?, ?, DATE('now'))
    """, (name, contact, diagnosis, anonymized_name, anonymized_contact))
    conn.commit()
    conn.close()


def get_all_patients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients")
    data = cur.fetchall()
    conn.close()
    return data


def delete_patient(patient_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM patients WHERE patient_id=?", (patient_id,))
    conn.commit()
    conn.close()


def update_patient(patient_id, name, contact, diagnosis):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE patients
        SET name=?, contact=?, diagnosis=?
        WHERE patient_id=?
    """, (name, contact, diagnosis, patient_id))
    conn.commit()
    conn.close()


def get_logs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    logs = cur.fetchall()
    conn.close()
    return logs
