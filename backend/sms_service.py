"""
HealthVerse AI — SMS OTP sender
Uses MSG91 or Twilio when configured; otherwise demo mode (return code to UI).
"""
import json
import urllib.request
import urllib.parse
import urllib.error

try:
    import config
except ImportError:
    class config:
        MSG91_AUTH_KEY = ""
        MSG91_TEMPLATE_ID = ""
        MSG91_SENDER_ID = "HVAI"
        TWILIO_ACCOUNT_SID = ""
        TWILIO_AUTH_TOKEN = ""
        TWILIO_FROM_NUMBER = ""
        USE_DEMO_OTP = True


def _has_msg91():
    return bool(getattr(config, "MSG91_AUTH_KEY", "") and getattr(config, "MSG91_TEMPLATE_ID", ""))


def _has_twilio():
    return bool(
        getattr(config, "TWILIO_ACCOUNT_SID", "")
        and getattr(config, "TWILIO_AUTH_TOKEN", "")
        and getattr(config, "TWILIO_FROM_NUMBER", "")
    )


def is_real_sms_enabled():
    return (_has_msg91() or _has_twilio()) and not getattr(config, "USE_DEMO_OTP", True)


def send_otp_sms(phone: str, code: str) -> dict:
    """
    Send OTP to phone. Returns {ok, mode, message, code?}
    In demo mode, includes code so UI can display it.
    """
    phone = phone.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        # Assume India if 10 digits
        if len(phone) == 10:
            phone = "+91" + phone
        elif phone.startswith("91") and len(phone) == 12:
            phone = "+" + phone

    if _has_msg91() and not getattr(config, "USE_DEMO_OTP", True):
        return _send_msg91(phone, code)
    if _has_twilio() and not getattr(config, "USE_DEMO_OTP", True):
        return _send_twilio(phone, code)

    # Demo mode
    return {
        "ok": True,
        "mode": "demo",
        "message": "Demo OTP (no SMS API keys configured). Code shown on screen.",
        "code": code,
    }


def _send_msg91(phone: str, code: str) -> dict:
    # MSG91 Flow API / sendotp style
    mobile = phone.lstrip("+")
    url = "https://control.msg91.com/api/v5/flow/"
    payload = {
        "template_id": config.MSG91_TEMPLATE_ID,
        "short_url": "0",
        "recipients": [
            {
                "mobiles": mobile,
                "var": code,  # template variable — adjust to your template var name
            }
        ],
    }
    # Also try classic OTP API as fallback path
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "authkey": config.MSG91_AUTH_KEY,
                "Content-Type": "application/json",
                "accept": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode())
            return {"ok": True, "mode": "msg91", "message": "OTP sent via MSG91", "raw": body}
    except Exception as e:
        # Fallback: simple SMS API
        try:
            q = urllib.parse.urlencode({
                "authkey": config.MSG91_AUTH_KEY,
                "mobiles": mobile,
                "message": f"Your HealthVerse AI OTP is {code}. Valid for 10 minutes.",
                "sender": getattr(config, "MSG91_SENDER_ID", "HVAI"),
                "route": "4",
            })
            req = urllib.request.Request(
                f"https://api.msg91.com/api/sendhttp.php?{q}",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return {"ok": True, "mode": "msg91", "message": "OTP sent via MSG91", "raw": resp.read().decode()}
        except Exception as e2:
            return {"ok": False, "mode": "msg91", "message": f"MSG91 failed: {e2}", "code": code}


def _send_twilio(phone: str, code: str) -> dict:
    import base64
    sid = config.TWILIO_ACCOUNT_SID
    token = config.TWILIO_AUTH_TOKEN
    from_num = config.TWILIO_FROM_NUMBER
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    data = urllib.parse.urlencode({
        "To": phone,
        "From": from_num,
        "Body": f"Your HealthVerse AI OTP is {code}. Valid for 10 minutes.",
    }).encode()
    auth_str = base64.b64encode(f"{sid}:{token}".encode()).decode()
    try:
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Basic {auth_str}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode())
            return {"ok": True, "mode": "twilio", "message": "OTP sent via Twilio", "sid": body.get("sid")}
    except Exception as e:
        return {"ok": False, "mode": "twilio", "message": f"Twilio failed: {e}", "code": code}
