"""
HealthVerse AI — Auth (password hashing + JWT + OTP)
Uses hashlib (stdlib) for PBKDF2. JWT is optional (simple base64 token if PyJWT missing).
"""
import hashlib
import secrets
import time
import base64
import json
import os

SECRET = os.environ.get("HV_SECRET", "healthverse-demo-secret-change-in-prod")
TOKEN_TTL = 72 * 3600  # 72 hours

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000)
    return salt + "$" + dk.hex()

def verify_password(password: str, stored: str) -> bool:
    if not stored or "$" not in stored:
        return False
    salt, h = stored.split("$", 1)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000)
    return secrets.compare_digest(dk.hex(), h)

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def _unb64(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)

def create_token(user_id: int, email: str) -> str:
    """Create a simple signed token (no external deps required)."""
    payload = {
        "uid": user_id,
        "email": email,
        "exp": int(time.time()) + TOKEN_TTL,
    }
    body = _b64(json.dumps(payload).encode())
    sig = hashlib.sha256((body + SECRET).encode()).hexdigest()[:32]
    return body + "." + sig

def decode_token(token: str):
    if not token or "." not in token:
        return None
    body, sig = token.rsplit(".", 1)
    expected = hashlib.sha256((body + SECRET).encode()).hexdigest()[:32]
    if not secrets.compare_digest(sig, expected):
        return None
    try:
        payload = json.loads(_unb64(body).decode())
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None

def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)
