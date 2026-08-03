"""
HealthVerse AI — SQLite Database Layer
"""
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "healthverse.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_column_exists(conn, table_name, column_name, column_def):
    columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()]
    if column_name not in columns:
        if "DEFAULT" in column_def.upper():
            def_type = column_def.split("DEFAULT", 1)[0].strip()
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {def_type}")
        else:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")


def backfill_user_columns(conn):
    conn.execute("UPDATE users SET is_email_verified = 1 WHERE is_email_verified IS NULL")
    conn.execute("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL OR updated_at = ''")


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn()
    cur = conn.cursor()

    users_exists = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
    if not users_exists:
        cur.executescript("""
        CREATE TABLE users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            email       TEXT UNIQUE,
            phone       TEXT UNIQUE,
            password_hash TEXT,
            name        TEXT NOT NULL,
            is_email_verified INTEGER DEFAULT 0,
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        );
        """)
    else:
        ensure_column_exists(conn, "users", "is_email_verified", "INTEGER")
        ensure_column_exists(conn, "users", "updated_at", "TEXT")
        backfill_user_columns(conn)

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS otp_verifications (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        otp_hash    TEXT NOT NULL,
        expires_at  TEXT NOT NULL,
        attempts    INTEGER DEFAULT 0,
        verified    INTEGER DEFAULT 0,
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS sessions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token       TEXT NOT NULL,
        expires_at  TEXT NOT NULL,
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS profiles (
        user_id     INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        age         INTEGER,
        gender      TEXT,
        blood_group TEXT,
        height_cm   REAL,
        weight_kg   REAL,
        allergies   TEXT DEFAULT 'None',
        diseases    TEXT DEFAULT 'None',
        emergency_contact TEXT,
        preferred_language TEXT DEFAULT 'en',
        updated_at  TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS reports (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        filename    TEXT,
        report_type TEXT DEFAULT 'lab',
        raw_text    TEXT,
        analysis    TEXT,          -- JSON
        translated  TEXT,          -- JSON {lang: text}
        risk_level  TEXT DEFAULT 'moderate',
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS medicines (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name        TEXT NOT NULL,
        dosage      TEXT,
        timing      TEXT,          -- morning / afternoon / night
        purpose     TEXT,
        taken_today INTEGER DEFAULT 0,
        created_at  TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS chat_messages (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        role        TEXT NOT NULL,  -- user / assistant
        content     TEXT NOT NULL,
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS appointments (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        doctor_name TEXT,
        specialty   TEXT,
        date        TEXT,
        time        TEXT,
        notes       TEXT,
        created_at  TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS health_metrics (
        user_id     INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        health_score INTEGER DEFAULT 75,
        water_liters REAL DEFAULT 0,
        water_target REAL DEFAULT 2.5,
        steps       INTEGER DEFAULT 0,
        steps_target INTEGER DEFAULT 7500,
        sleep_hours REAL DEFAULT 0,
        medicine_adherence REAL DEFAULT 0
    );
    """)
    conn.commit()
    conn.close()
    print(f"[DB] Initialized at {DB_PATH}")


def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


# ── Users ──────────────────────────────────────────────
def create_user(name, email=None, phone=None, password_hash=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email, phone, password_hash, is_email_verified, updated_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
        (name, email, phone, password_hash, 1 if email else 0)
    )
    uid = cur.lastrowid
    # empty profile + metrics
    cur.execute("INSERT INTO profiles (user_id) VALUES (?)", (uid,))
    cur.execute("INSERT INTO health_metrics (user_id) VALUES (?)", (uid,))
    # seed sample medicines
    sample_meds = [
        ("Metformin 500mg", "1 tablet after breakfast", "morning", "Controls blood sugar"),
        ("Amlodipine 5mg", "1 tablet after lunch", "afternoon", "Lowers blood pressure"),
        ("Atorvastatin 10mg", "1 tablet at bedtime", "night", "Reduces cholesterol"),
    ]
    for m in sample_meds:
        cur.execute(
            "INSERT INTO medicines (user_id, name, dosage, timing, purpose) VALUES (?,?,?,?,?)",
            (uid, *m)
        )
    # sample appointment
    cur.execute(
        "INSERT INTO appointments (user_id, doctor_name, specialty, date, time) VALUES (?,?,?,?,?)",
        (uid, "Dr. Priya Sharma", "Cardiology Follow-up", "2026-08-02", "10:30 AM")
    )
    conn.commit()
    conn.close()
    return uid


def get_user_by_email(email):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row_to_dict(row)


def get_user_by_phone(phone):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
    conn.close()
    return row_to_dict(row)


def get_user_by_id(uid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    conn.close()
    return row_to_dict(row)


def update_user_password(uid, password_hash):
    conn = get_conn()
    conn.execute("UPDATE users SET password_hash = ?, updated_at = datetime('now') WHERE id = ?", (password_hash, uid))
    conn.commit()
    conn.close()


def save_otp(user_id, otp_hash, expires_at):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM otp_verifications WHERE user_id = ?", (user_id,))
    cur.execute(
        "INSERT INTO otp_verifications (user_id, otp_hash, expires_at, attempts, verified) VALUES (?, ?, ?, 0, 0)",
        (user_id, otp_hash, expires_at)
    )
    oid = cur.lastrowid
    conn.commit()
    conn.close()
    return oid


def get_active_otp(user_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM otp_verifications WHERE user_id = ? AND verified = 0 ORDER BY id DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    conn.close()
    return row_to_dict(row)


def increment_otp_attempts(otp_id):
    conn = get_conn()
    conn.execute("UPDATE otp_verifications SET attempts = attempts + 1 WHERE id = ?", (otp_id,))
    conn.commit()
    conn.close()


def mark_otp_used(otp_id):
    conn = get_conn()
    conn.execute("UPDATE otp_verifications SET verified = 1 WHERE id = ?", (otp_id,))
    conn.commit()
    conn.close()


def create_session(user_id, token, expires_at):
    conn = get_conn()
    conn.execute("INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)", (user_id, token, expires_at))
    conn.commit()
    conn.close()


def get_session(token):
    conn = get_conn()
    row = conn.execute("SELECT * FROM sessions WHERE token = ?", (token,)).fetchone()
    conn.close()
    return row_to_dict(row)


def invalidate_sessions(user_id):
    conn = get_conn()
    conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# ── Profile ────────────────────────────────────────────
def update_profile(uid, data: dict):
    conn = get_conn()
    fields = []
    vals = []
    allowed = ["age", "gender", "blood_group", "height_cm", "weight_kg",
               "allergies", "diseases", "emergency_contact", "preferred_language"]
    for k in allowed:
        if k in data:
            fields.append(f"{k} = ?")
            vals.append(data[k])
    if not fields:
        conn.close()
        return
    fields.append("updated_at = datetime('now')")
    vals.append(uid)
    conn.execute(f"UPDATE profiles SET {', '.join(fields)} WHERE user_id = ?", vals)
    # also update name on users if provided
    if "name" in data:
        conn.execute("UPDATE users SET name = ? WHERE id = ?", (data["name"], uid))
    conn.commit()
    conn.close()


def get_profile(uid):
    conn = get_conn()
    user = conn.execute("SELECT id, name, email, phone, created_at FROM users WHERE id = ?", (uid,)).fetchone()
    profile = conn.execute("SELECT * FROM profiles WHERE user_id = ?", (uid,)).fetchone()
    conn.close()
    if not user:
        return None
    result = row_to_dict(user)
    if profile:
        result.update(row_to_dict(profile))
    return result


# ── Reports ────────────────────────────────────────────
def save_report(uid, filename, raw_text, analysis: dict, risk_level="moderate"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO reports (user_id, filename, raw_text, analysis, risk_level) VALUES (?,?,?,?,?)",
        (uid, filename, raw_text, json.dumps(analysis), risk_level)
    )
    rid = cur.lastrowid
    conn.commit()
    conn.close()
    return rid


def get_reports(uid, limit=20):
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, filename, report_type, risk_level, analysis, created_at FROM reports WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (uid, limit)
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = row_to_dict(r)
        if d.get("analysis"):
            try:
                d["analysis"] = json.loads(d["analysis"])
            except Exception:
                pass
        result.append(d)
    return result


def get_report(uid, rid):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM reports WHERE id = ? AND user_id = ?", (rid, uid)
    ).fetchone()
    conn.close()
    d = row_to_dict(row)
    if d and d.get("analysis"):
        try:
            d["analysis"] = json.loads(d["analysis"])
        except Exception:
            pass
    return d


def save_translation(rid, lang, text):
    conn = get_conn()
    row = conn.execute("SELECT translated FROM reports WHERE id = ?", (rid,)).fetchone()
    translated = {}
    if row and row["translated"]:
        try:
            translated = json.loads(row["translated"])
        except Exception:
            pass
    translated[lang] = text
    conn.execute("UPDATE reports SET translated = ? WHERE id = ?", (json.dumps(translated), rid))
    conn.commit()
    conn.close()


# ── Medicines ──────────────────────────────────────────
def get_medicines(uid):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM medicines WHERE user_id = ?", (uid,)).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def mark_medicine_taken(uid, med_id, taken=True):
    conn = get_conn()
    conn.execute(
        "UPDATE medicines SET taken_today = ? WHERE id = ? AND user_id = ?",
        (1 if taken else 0, med_id, uid)
    )
    conn.commit()
    conn.close()


# ── Chat ───────────────────────────────────────────────
def save_chat(uid, role, content):
    conn = get_conn()
    conn.execute(
        "INSERT INTO chat_messages (user_id, role, content) VALUES (?,?,?)",
        (uid, role, content)
    )
    conn.commit()
    conn.close()


def get_chat_history(uid, limit=50):
    conn = get_conn()
    rows = conn.execute(
        "SELECT role, content, created_at FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (uid, limit)
    ).fetchall()
    conn.close()
    return [row_to_dict(r) for r in reversed(rows)]


# ── Dashboard ──────────────────────────────────────────
def get_dashboard(uid):
    conn = get_conn()
    metrics = row_to_dict(conn.execute("SELECT * FROM health_metrics WHERE user_id = ?", (uid,)).fetchone())
    meds = [row_to_dict(r) for r in conn.execute("SELECT * FROM medicines WHERE user_id = ?", (uid,)).fetchall()]
    appts = [row_to_dict(r) for r in conn.execute(
        "SELECT * FROM appointments WHERE user_id = ? ORDER BY date LIMIT 5", (uid,)
    ).fetchall()]
    reports_count = conn.execute("SELECT COUNT(*) as c FROM reports WHERE user_id = ?", (uid,)).fetchone()["c"]
    conn.close()
    if metrics and meds:
        taken = sum(1 for m in meds if m.get("taken_today"))
        metrics["medicine_adherence"] = round((taken / len(meds)) * 100, 1) if meds else 0
    return {
        "metrics": metrics or {},
        "medicines": meds,
        "appointments": appts,
        "reports_count": reports_count
    }


def update_metric(uid, field, value):
    allowed = ["health_score", "water_liters", "steps", "sleep_hours", "medicine_adherence"]
    if field not in allowed:
        return False
    conn = get_conn()
    conn.execute(f"UPDATE health_metrics SET {field} = ? WHERE user_id = ?", (value, uid))
    conn.commit()
    conn.close()
    return True
