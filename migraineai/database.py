"""
database.py  —  Pure sqlite3 database layer (no ORM needed)
Tables:
  users           — registered users
  assessments     — each risk assessment submission
  symptom_logs    — daily symptom diary entries
  recommendations — AI recommendations per assessment
"""

import sqlite3
import os

DB_PATH = "data/migraineai.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            age           INTEGER,
            gender        TEXT,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL REFERENCES users(id),
            submitted_at     TEXT    DEFAULT (datetime('now')),
            age              INTEGER,
            duration         INTEGER,
            frequency        INTEGER,
            location         INTEGER,
            character        INTEGER,
            intensity        INTEGER,
            nausea           INTEGER,
            vomit            INTEGER,
            phonophobia      INTEGER,
            photophobia      INTEGER,
            visual           INTEGER,
            sensory          INTEGER,
            dysphasia        INTEGER,
            dysarthria       INTEGER,
            vertigo          INTEGER,
            tinnitus         INTEGER,
            hypoacusis       INTEGER,
            diplopia         INTEGER,
            defect           INTEGER,
            ataxia           INTEGER,
            conscience       INTEGER,
            paresthesia      INTEGER,
            dpf              INTEGER,
            sleep_duration   REAL,
            sleep_quality    INTEGER,
            physical_activity INTEGER,
            stress_level     INTEGER,
            bmi              REAL,
            bp_systolic      INTEGER,
            heart_rate       INTEGER,
            daily_steps      INTEGER,
            sleep_disorder   INTEGER,
            predicted_type   TEXT,
            risk_score       INTEGER,
            attack_prob      INTEGER,
            chronic_risk     INTEGER,
            risk_category    TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS symptom_logs (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id            INTEGER NOT NULL REFERENCES users(id),
            logged_at          TEXT    DEFAULT (datetime('now')),
            headache_severity  INTEGER,
            duration_hrs       REAL,
            triggers           TEXT,
            medication_taken   TEXT,
            notes              TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL REFERENCES assessments(id),
            icon          TEXT,
            message       TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialised →", DB_PATH)

# ── USERS ─────────────────────────────────────────────────────────────────────
def create_user(name, email, password_hash, age=None, gender=None):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash, age, gender) VALUES (?,?,?,?,?)",
            (name, email, password_hash, age, gender)
        )
        conn.commit()
        return True, "User created"
    except sqlite3.IntegrityError:
        return False, "Email already registered"
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(uid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return dict(row) if row else None

# ── ASSESSMENTS ───────────────────────────────────────────────────────────────
def save_assessment(user_id, features: dict, result: dict, recommendations: list):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO assessments (
            user_id, age, duration, frequency, location, character,
            intensity, nausea, vomit, phonophobia, photophobia,
            visual, sensory, dysphasia, dysarthria, vertigo,
            tinnitus, hypoacusis, diplopia, defect, ataxia,
            conscience, paresthesia, dpf,
            sleep_duration, sleep_quality, physical_activity,
            stress_level, bmi, bp_systolic, heart_rate,
            daily_steps, sleep_disorder,
            predicted_type, risk_score, attack_prob,
            chronic_risk, risk_category
        ) VALUES (
            :user_id,:age,:duration,:frequency,:location,:character,
            :intensity,:nausea,:vomit,:phonophobia,:photophobia,
            :visual,:sensory,:dysphasia,:dysarthria,:vertigo,
            :tinnitus,:hypoacusis,:diplopia,:defect,:ataxia,
            :conscience,:paresthesia,:dpf,
            :sleep_duration,:sleep_quality,:physical_activity,
            :stress_level,:bmi,:bp_systolic,:heart_rate,
            :daily_steps,:sleep_disorder,
            :predicted_type,:risk_score,:attack_prob,
            :chronic_risk,:risk_category
        )
    """, {
        "user_id": user_id,
        **{k.lower(): v for k, v in features.items()},
        **result
    })
    assessment_id = c.lastrowid
    for rec in recommendations:
        c.execute(
            "INSERT INTO recommendations (assessment_id, icon, message) VALUES (?,?,?)",
            (assessment_id, rec["icon"], rec["text"])
        )
    conn.commit()
    conn.close()
    return assessment_id

def get_user_assessments(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM assessments WHERE user_id=? ORDER BY submitted_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_assessment_with_recs(assessment_id):
    conn = get_conn()
    a    = conn.execute("SELECT * FROM assessments WHERE id=?", (assessment_id,)).fetchone()
    recs = conn.execute("SELECT * FROM recommendations WHERE assessment_id=?", (assessment_id,)).fetchall()
    conn.close()
    return dict(a) if a else None, [dict(r) for r in recs]

def get_trend_data(user_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT submitted_at, risk_score, attack_prob, chronic_risk,
               stress_level, sleep_duration, frequency
        FROM assessments WHERE user_id=?
        ORDER BY submitted_at ASC LIMIT 10
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── SYMPTOM LOGS ──────────────────────────────────────────────────────────────
def add_symptom_log(user_id, severity, duration_hrs, triggers, medication, notes):
    conn = get_conn()
    conn.execute("""
        INSERT INTO symptom_logs
        (user_id, headache_severity, duration_hrs, triggers, medication_taken, notes)
        VALUES (?,?,?,?,?,?)
    """, (user_id, severity, duration_hrs, triggers, medication, notes))
    conn.commit()
    conn.close()

def get_symptom_logs(user_id, limit=30):
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM symptom_logs WHERE user_id=?
        ORDER BY logged_at DESC LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_symptom_summary(user_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT COUNT(*) AS total_entries,
               ROUND(AVG(headache_severity),1) AS avg_severity,
               MAX(headache_severity) AS max_severity,
               ROUND(AVG(duration_hrs),1) AS avg_duration
        FROM symptom_logs WHERE user_id=?
    """, (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else {}