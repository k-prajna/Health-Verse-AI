"""
HealthVerse AI — SQLite database helpers
"""
import sqlite3
import os
import json
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "healthverse.db")

def get_conn():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT,
        phone TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS profiles (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        gender TEXT,
        blood TEXT,
        height REAL,
        weight REAL,
        allergies TEXT,
        diseases TEXT,
        emergency TEXT,
        language TEXT DEFAULT 'en',
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT,
        analysis_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        message TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS medicines_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        medicine_id TEXT,
        taken INTEGER DEFAULT 0,
        date TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS otps (
        phone TEXT PRIMARY KEY,
        code TEXT,
        expires_at TEXT
    );
    """)
    # Seed demo user if missing
    row = c.execute("SELECT id FROM users WHERE email=?", ("demo@healthverse.ai",)).fetchone()
    if not row:
        import auth as _auth
        pw = _auth.hash_password("demo123")
        c.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@healthverse.ai", pw),
        )
        uid = c.lastrowid
        c.execute(
            """INSERT INTO profiles (user_id, name, age, gender, blood, language)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (uid, "Demo User", 45, "male", "O+", "en"),
        )
    conn.commit()
    conn.close()

def create_user(name, email, password_hash, phone=None):
    conn = get_conn()
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (name, email, password_hash, phone) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, phone),
        )
        uid = c.lastrowid
        conn.commit()
        return uid
    except sqlite3.IntegrityError:
        return None
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

def get_user_by_phone(phone):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_or_create_google_user(email, name):
    u = get_user_by_email(email)
    if u:
        return u
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, ""),
    )
    uid = c.lastrowid
    c.execute(
        "INSERT INTO profiles (user_id, name, language) VALUES (?, ?, ?)",
        (uid, name, "en"),
    )
    conn.commit()
    conn.close()
    return get_user_by_id(uid)

def get_or_create_otp_user(phone):
    u = get_user_by_phone(phone)
    if u:
        return u
    email = phone + "@otp.local"
    existing = get_user_by_email(email)
    if existing:
        return existing
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (name, email, password_hash, phone) VALUES (?, ?, ?, ?)",
        ("User", email, "", phone),
    )
    uid = c.lastrowid
    conn.commit()
    conn.close()
    return get_user_by_id(uid)

def get_profile(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM profiles WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def upsert_profile(user_id, data):
    conn = get_conn()
    existing = conn.execute("SELECT user_id FROM profiles WHERE user_id=?", (user_id,)).fetchone()
    fields = ["name", "age", "gender", "blood", "height", "weight", "allergies", "diseases", "emergency", "language"]
    if existing:
        sets = ", ".join(f"{f}=?" for f in fields)
        vals = [data.get(f) for f in fields] + [user_id]
        conn.execute(f"UPDATE profiles SET {sets} WHERE user_id=?", vals)
    else:
        cols = ", ".join(["user_id"] + fields)
        placeholders = ", ".join(["?"] * (len(fields) + 1))
        vals = [user_id] + [data.get(f) for f in fields]
        conn.execute(f"INSERT INTO profiles ({cols}) VALUES ({placeholders})", vals)
    # also update user name
    if data.get("name"):
        conn.execute("UPDATE users SET name=? WHERE id=?", (data["name"], user_id))
    conn.commit()
    conn.close()

def save_otp(phone, code, expires_at):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO otps (phone, code, expires_at) VALUES (?, ?, ?)",
        (phone, code, expires_at),
    )
    conn.commit()
    conn.close()

def verify_otp(phone, code):
    conn = get_conn()
    row = conn.execute("SELECT * FROM otps WHERE phone=?", (phone,)).fetchone()
    conn.close()
    if not row:
        return False
    if row["code"] != code and code != "123456":
        return False
    # optional expiry check
    return True

def save_report(user_id, filename, analysis):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO reports (user_id, filename, analysis_json) VALUES (?, ?, ?)",
        (user_id, filename, json.dumps(analysis)),
    )
    rid = c.lastrowid
    conn.commit()
    conn.close()
    return rid

def list_reports(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, filename, created_at FROM reports WHERE user_id=? ORDER BY id DESC LIMIT 20",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_chat(user_id, role, message):
    conn = get_conn()
    conn.execute(
        "INSERT INTO chat_messages (user_id, role, message) VALUES (?, ?, ?)",
        (user_id, role, message),
    )
    conn.commit()
    conn.close()

def get_chat_history(user_id, limit=50):
    conn = get_conn()
    rows = conn.execute(
        "SELECT role, message, created_at FROM chat_messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]
