"""
HealthVerse AI — Authentication (JWT + salted password hash + email OTP)
"""
import hashlib
import re
import secrets
import smtplib
import time
from datetime import datetime, timedelta
from email.message import EmailMessage
from os import getenv

try:
    import jwt
except ImportError:
    try:
        from jose import jwt
    except ImportError:
        jwt = None

JWT_SECRET = getenv("JWT_SECRET", "healthverse-ai-demo-secret-key-change-in-prod-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(getenv("JWT_EXPIRE_HOURS", "72"))
OTP_TTL_SECONDS = int(getenv("OTP_TTL_SECONDS", "300"))
OTP_MAX_ATTEMPTS = int(getenv("OTP_MAX_ATTEMPTS", "5"))
OTP_RESEND_COOLDOWN_SECONDS = int(getenv("OTP_RESEND_COOLDOWN_SECONDS", "30"))
_otp_resend_state = {}


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))


def hash_password(password: str, salt: str = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${hashed.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, hashed = stored.split("$", 1)
        check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
        return check.hex() == hashed
    except Exception:
        return False


def is_strong_password(password: str) -> bool:
    if not password or len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[^A-Za-z0-9]", password):
        return False
    return True


def create_token(user_id: int, name: str, email: str = None) -> str:
    payload = {
        "sub": user_id,
        "name": name,
        "email": email,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXPIRE_HOURS * 3600,
    }
    if jwt:
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    import base64, json
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


def decode_token(token: str) -> dict | None:
    try:
        if jwt:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        import base64, json
        return json.loads(base64.urlsafe_b64decode(token.encode()))
    except Exception:
        return None


def hash_otp(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def verify_otp_code(code: str, stored_hash: str) -> bool:
    if not code or not stored_hash:
        return False
    return hash_otp(code) == stored_hash


def generate_otp_code() -> str:
    return f"{secrets.randbelow(10**6):06d}"


def can_resend_otp(email: str) -> bool:
    now = time.time()
    last = _otp_resend_state.get((email or "").lower())
    if last and now - last < OTP_RESEND_COOLDOWN_SECONDS:
        return False
    return True


def record_otp_resend(email: str) -> None:
    _otp_resend_state[(email or "").lower()] = time.time()


def send_otp_email(to_email: str, otp_code: str) -> bool:
    smtp_host = getenv("SMTP_HOST")
    smtp_port = getenv("SMTP_PORT")
    smtp_username = getenv("SMTP_USERNAME")
    smtp_password = getenv("SMTP_PASSWORD")
    email_from = getenv("EMAIL_FROM", smtp_username or "no-reply@healthverse.ai")

    if not smtp_host or not smtp_port or not smtp_username or not smtp_password:
        return False

    msg = EmailMessage()
    msg["Subject"] = "HealthVerse Insight — Your Login Verification Code"
    msg["From"] = email_from
    msg["To"] = to_email
    msg.set_content(
        f"Hello,\n\nYour HealthVerse Insight login verification code is:\n\n{otp_code}\n\n"
        "This code will expire in 5 minutes.\n\nIf you did not attempt to log in, please secure your account.\n\nRegards,\nHealthVerse Insight Team"
    )

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        return True
    except Exception:
        return False


# ── Google OAuth ID Token verification ─────────────────
# Set your Web Client ID from Google Cloud Console.
# Leave empty to keep demo/fake Google accounts working.
GOOGLE_CLIENT_ID = ""  # e.g. "123456789-abcdef.apps.googleusercontent.com"


def verify_google_id_token(id_token: str) -> dict | None:
    """
    Verify a Google ID token using Google's tokeninfo endpoint.
    Returns payload dict (email, name, sub, picture, ...) or None on failure.
    Requires internet on the machine running the backend.
    """
    if not id_token:
        return None
    try:
        import requests
        # tokeninfo is simple and sufficient for most apps
        url = "https://oauth2.googleapis.com/tokeninfo"
        resp = requests.get(url, params={"id_token": id_token}, timeout=8)
        if resp.status_code != 200:
            return None
        data = resp.json()
        # Basic validation
        if data.get("error"):
            return None
        aud = data.get("aud") or data.get("azp")
        if GOOGLE_CLIENT_ID and aud != GOOGLE_CLIENT_ID:
            # If client ID is configured, enforce audience match
            return None
        if data.get("email_verified") not in (True, "true", "1"):
            # Prefer verified emails
            pass  # still allow for some demo accounts
        return {
            "sub": data.get("sub"),
            "email": data.get("email"),
            "name": data.get("name") or data.get("email", "").split("@")[0],
            "picture": data.get("picture"),
            "email_verified": data.get("email_verified") in (True, "true", "1"),
            "iss": data.get("iss"),
        }
    except Exception as e:
        print(f"[Auth] Google token verify failed: {e}")
        return None
