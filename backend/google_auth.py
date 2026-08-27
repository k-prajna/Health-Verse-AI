"""
Verify Google ID tokens using Google's tokeninfo endpoint (stdlib only).
"""
import json
import urllib.request
import urllib.error

try:
    import config
    GOOGLE_CLIENT_ID = getattr(config, "GOOGLE_CLIENT_ID", "") or ""
except ImportError:
    GOOGLE_CLIENT_ID = ""


def verify_google_id_token(id_token: str) -> dict:
    """
    Returns {ok, email, name, picture, sub} or {ok: False, error: ...}
    """
    if not id_token:
        return {"ok": False, "error": "Missing id_token"}
    try:
        url = "https://oauth2.googleapis.com/tokeninfo?id_token=" + urllib.parse.quote(id_token)
        # urllib.parse needed
        import urllib.parse
        url = "https://oauth2.googleapis.com/tokeninfo?id_token=" + urllib.parse.quote(id_token)
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        # Validate audience if client id is set
        aud = data.get("aud", "")
        if GOOGLE_CLIENT_ID and aud != GOOGLE_CLIENT_ID:
            return {"ok": False, "error": "Token audience mismatch. Check GOOGLE_CLIENT_ID."}
        email = data.get("email")
        if not email:
            return {"ok": False, "error": "No email in token"}
        if data.get("email_verified") in ("false", False):
            return {"ok": False, "error": "Email not verified by Google"}
        return {
            "ok": True,
            "email": email,
            "name": data.get("name") or data.get("given_name") or email.split("@")[0],
            "picture": data.get("picture"),
            "sub": data.get("sub"),
        }
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"Invalid Google token ({e.code})"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
