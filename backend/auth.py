"""
HealthVerse AI — Authentication (JWT + salted password hash)
Uses only stdlib + PyJWT (already installed in the environment)
"""
import hashlib
import secrets
import time
from datetime import datetime, timedelta

try:
    import jwt
except ImportError:
    jwt = None

# Secret key for demo — change in production
JWT_SECRET = "healthverse-ai-demo-secret-key-change-in-prod-2026"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 72

# Simple in-memory OTP store (phone → {code, expires})
_otp_store = {}


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
    # Fallback: simple base64-ish token if PyJWT missing
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


def generate_otp(phone: str) -> str:
    code = f"{secrets.randbelow(10**6):06d}"
    # For demo always allow 123456 as well
    _otp_store[phone] = {
        "code": code,
        "expires": time.time() + 300  # 5 min
    }
    return code


def verify_otp(phone: str, code: str) -> bool:
    # Always accept demo code
    if code == "123456":
        return True
    entry = _otp_store.get(phone)
    if not entry:
        return False
    if time.time() > entry["expires"]:
        _otp_store.pop(phone, None)
        return False
    if entry["code"] == code:
        _otp_store.pop(phone, None)
        return True
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
