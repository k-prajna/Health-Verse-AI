#!/usr/bin/env python3
"""
HealthVerse AI — HTTP server (stdlib only)
Serves API at /api/* and static frontend from parent directory.
"""

import os
import sys
import json
import mimetypes

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone


# ============================================================
# PATH SETUP
# ============================================================

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)

sys.path.insert(0, BACKEND_DIR)


# ============================================================
# IMPORTS
# ============================================================

import database as db
import auth
import ai_service

try:
    import config as app_config
except ImportError:
    app_config = None

try:
    import sms_service
except ImportError:
    sms_service = None

try:
    import google_auth
except ImportError:
    google_auth = None


# ============================================================
# CONFIGURATION
# ============================================================

UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")
DATA_DIR = os.path.join(BACKEND_DIR, "data")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

PORT = int(
    os.environ.get(
        "PORT",
        getattr(app_config, "PORT", 8000) if app_config else 8000
    )
)

GOOGLE_CLIENT_ID = (
    getattr(app_config, "GOOGLE_CLIENT_ID", "")
    if app_config
    else ""
) or ""


# ============================================================
# JSON RESPONSE
# ============================================================

def json_response(handler, status, data):
    body = json.dumps(data).encode("utf-8")

    handler.send_response(status)

    handler.send_header(
        "Content-Type",
        "application/json; charset=utf-8"
    )

    handler.send_header(
        "Content-Length",
        str(len(body))
    )

    handler.send_header(
        "Access-Control-Allow-Origin",
        "*"
    )

    handler.send_header(
        "Access-Control-Allow-Headers",
        "Content-Type, Authorization"
    )

    handler.send_header(
        "Access-Control-Allow-Methods",
        "GET, POST, PUT, OPTIONS"
    )

    handler.end_headers()

    handler.wfile.write(body)


# ============================================================
# READ JSON REQUEST
# ============================================================

def read_json(handler):
    length = int(
        handler.headers.get("Content-Length", 0)
    )

    if length == 0:
        return {}

    raw = handler.rfile.read(length)

    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return {}


# ============================================================
# AUTHENTICATED USER
# ============================================================

def get_user_from_auth(handler):

    header = handler.headers.get(
        "Authorization",
        ""
    )

    if not header.startswith("Bearer "):
        return None

    token = header[7:].strip()

    payload = auth.decode_token(token)

    if not payload:
        return None

    return db.get_user_by_id(
        payload["uid"]
    )


# ============================================================
# HTTP HANDLER
# ============================================================

class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):

        sys.stderr.write(
            "[%s] %s\n"
            % (
                self.log_date_time_string(),
                fmt % args
            )
        )

    # ========================================================
    # OPTIONS
    # ========================================================

    def do_OPTIONS(self):

        self.send_response(204)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, PUT, OPTIONS"
        )

        self.end_headers()

    # ========================================================
    # GET
    # ========================================================

    def do_GET(self):

        parsed = urlparse(self.path)
        path = parsed.path

        # ---------------- API ----------------

        if path.startswith("/api/"):

            self.handle_api_get(path)

            return

        # ---------------- STATIC FILES ----------------

        if path == "/" or path == "":
            path = "/index.html"

        file_path = os.path.normpath(
            os.path.join(
                ROOT_DIR,
                path.lstrip("/")
            )
        )

        if not file_path.startswith(ROOT_DIR):

            self.send_error(403)

            return

        if not os.path.isfile(file_path):

            # SPA fallback

            file_path = os.path.join(
                ROOT_DIR,
                "index.html"
            )

            if not os.path.isfile(file_path):

                self.send_error(404)

                return

        content_type = (
            mimetypes.guess_type(file_path)[0]
            or "application/octet-stream"
        )

        try:

            with open(file_path, "rb") as file:

                data = file.read()

            self.send_response(200)

            self.send_header(
                "Content-Type",
                content_type
            )

            self.send_header(
                "Content-Length",
                str(len(data))
            )

            self.end_headers()

            self.wfile.write(data)

        except Exception:

            self.send_error(500)

    # ========================================================
    # POST
    # ========================================================

    def do_POST(self):

        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):

            self.handle_api_post(path)

        else:

            json_response(
                self,
                404,
                {"error": "Not found"}
            )

    # ========================================================
    # PUT
    # ========================================================

    def do_PUT(self):

        parsed = urlparse(self.path)

        if parsed.path.startswith("/api/"):

            self.handle_api_put(
                parsed.path
            )

        else:

            json_response(
                self,
                404,
                {"error": "Not found"}
            )

    # ========================================================
    # API GET
    # ========================================================

    def handle_api_get(self, path):

        # ---------------- HEALTH ----------------

        if path == "/api/health":

            return json_response(
                self,
                200,
                {
                    "status": "ok",
                    "service": "HealthVerse AI",
                    "google_client_id": GOOGLE_CLIENT_ID,
                    "real_sms": bool(
                        sms_service
                        and sms_service.is_real_sms_enabled()
                    ),
                }
            )

        # ---------------- CONFIG ----------------

        if path == "/api/config":

            return json_response(
                self,
                200,
                {
                    "google_client_id": GOOGLE_CLIENT_ID,
                    "real_sms": bool(
                        sms_service
                        and sms_service.is_real_sms_enabled()
                    ),
                }
            )

        # ---------------- CURRENT USER ----------------

        user = get_user_from_auth(self)

        # ---------------- PROFILE ----------------

        if path == "/api/profile":

            if not user:

                return json_response(
                    self,
                    401,
                    {"error": "Unauthorized"}
                )

            profile = (
                db.get_profile(user["id"])
                or {}
            )

            return json_response(
                self,
                200,
                {
                    "profile": profile,
                    "user": {
                        "id": user["id"],
                        "name": user["name"],
                        "email": user["email"],
                    },
                }
            )

        # ---------------- REPORTS ----------------

        if path == "/api/reports":

            if not user:

                return json_response(
                    self,
                    401,
                    {"error": "Unauthorized"}
                )

            return json_response(
                self,
                200,
                {
                    "reports": db.list_reports(
                        user["id"]
                    )
                }
            )

        # ---------------- CHAT HISTORY ----------------

        if path == "/api/chat/history":

            if not user:

                return json_response(
                    self,
                    401,
                    {"error": "Unauthorized"}
                )

            return json_response(
                self,
                200,
                {
                    "messages": db.get_chat_history(
                        user["id"]
                    )
                }
            )

        # ---------------- MEDICINES ----------------

        if path == "/api/medicines":

            return json_response(
                self,
                200,
                {
                    "medicines": [
                        {
                            "id": "1",
                            "name": "Metformin 500mg",
                            "time": "after breakfast",
                        },
                        {
                            "id": "2",
                            "name": "Amlodipine 5mg",
                            "time": "after lunch",
                        },
                        {
                            "id": "3",
                            "name": "Atorvastatin 10mg",
                            "time": "at bedtime",
                        },
                    ]
                }
            )

        # ---------------- DASHBOARD ----------------

        if path == "/api/dashboard":

            return json_response(
                self,
                200,
                {
                    "health_score": 78,
                    "adherence": 85,
                    "water": {
                        "current": 1.5,
                        "target": 2.5,
                    },
                    "steps": {
                        "current": 5400,
                        "target": 7500,
                    },
                    "sleep": 7.2,
                }
            )

        # ---------------- LOGIN STATISTICS ----------------

        if path == "/api/admin/login-stats":

            try:

                stats = db.get_login_stats()

                return json_response(
                    self,
                    200,
                    stats
                )

            except AttributeError:

                return json_response(
                    self,
                    500,
                    {
                        "error": (
                            "get_login_stats() is missing "
                            "from database.py"
                        )
                    }
                )

        # ---------------- 404 ----------------

        return json_response(
            self,
            404,
            {"error": "Not found"}
        )

    # ========================================================
    # API POST
    # ========================================================

    def handle_api_post(self, path):

        body = read_json(self)

        # ====================================================
        # REGISTER
        # ====================================================

        if path == "/api/auth/register":

            name = (
                body.get("name") or ""
            ).strip()

            email = (
                body.get("email") or ""
            ).strip().lower()

            password = (
                body.get("password") or ""
            )

            if not name or not email or not password:

                return json_response(
                    self,
                    400,
                    {
                        "error":
                        "Name, email, password required"
                    }
                )

            if len(password) < 6:

                return json_response(
                    self,
                    400,
                    {
                        "error":
                        "Password must be at least 6 characters"
                    }
                )

            if db.get_user_by_email(email):

                return json_response(
                    self,
                    400,
                    {
                        "error":
                        "Email already registered"
                    }
                )

            password_hash = auth.hash_password(
                password
            )

            uid = db.create_user(
                name,
                email,
                password_hash
            )

            if not uid:

                return json_response(
                    self,
                    400,
                    {
                        "error":
                        "Could not create user"
                    }
                )

            token = auth.create_token(
                uid,
                email
            )

            return json_response(
                self,
                201,
                {
                    "token": token,
                    "user": {
                        "id": uid,
                        "name": name,
                        "email": email,
                    },
                }
            )

        # ====================================================
        # PASSWORD LOGIN
        # ====================================================

        if path == "/api/auth/login":

            email = (
                body.get("email") or ""
            ).strip().lower()

            password = (
                body.get("password") or ""
            )

            user = db.get_user_by_email(
                email
            )

            if (
                not user
                or not auth.verify_password(
                    password,
                    user.get("password_hash") or ""
                )
            ):

                return json_response(
                    self,
                    401,
                    {
                        "error":
                        "Invalid email or password"
                    }
                )

            token = auth.create_token(
                user["id"],
                user["email"]
            )

            # Record successful login
            try:
                db.record_login(
                    user["id"],
                    "password"
                )
            except AttributeError:
                pass

            profile = db.get_profile(
                user["id"]
            )

            return json_response(
                self,
                200,
                {
                    "token": token,
                    "user": {
                        "id": user["id"],
                        "name": user["name"],
                        "email": user["email"],
                    },
                    "profile": profile,
                }
            )

        # ====================================================
        # OTP SEND
        # ====================================================

        if path == "/api/auth/otp/send":

            phone = (
                body.get("phone") or ""
            ).strip()

            clean_phone = (
                phone
                .replace(" ", "")
                .replace("-", "")
                .replace("+", "")
            )

            if (
                not phone
                or len(clean_phone) < 10
            ):

                return json_response(
                    self,
                    400,
                    {
                        "error":
                        "Valid phone required"
                    }
                )

            code = auth.generate_otp()

            expires = (
                datetime.now(timezone.utc)
                + timedelta(minutes=10)
            ).isoformat()

            db.save_otp(
                phone,
                code,
                expires
            )

            if sms_service:

                result = sms_service.send_otp_sms(
                    phone,
                    code
                )

                response = {
                    "ok": result.get(
                        "ok",
                        True
                    ),
                    "message": result.get(
                        "message",
                        "OTP sent"
                    ),
                    "mode": result.get(
                        "mode",
                        "demo"
                    ),
                }

                # Demo mode shows OTP
                if (
                    result.get("mode") == "demo"
                    or result.get("code")
                ):

                    response["code"] = (
                        result.get("code")
                        or code
                    )

                if not result.get("ok"):

                    response["code"] = code

                    response["message"] = result.get(
                        "message",
                        "SMS failed; use shown code"
                    )

                return json_response(
                    self,
                    200,
                    response
                )

            return json_response(
                self,
                200,
                {
                    "ok": True,
                    "message": "OTP sent (demo)",
                    "mode": "demo",
                    "code": code,
                }
            )

        # ====================================================
        # OTP VERIFY
        # ====================================================

        if path == "/api/auth/otp/verify":

            phone = (
                body.get("phone") or ""
            ).strip()

            code = (
                body.get("code") or ""
            ).strip()

            if not db.verify_otp(
                phone,
                code
            ):

                return json_response(
                    self,
                    401,
                    {
                        "error":
                        "Invalid OTP"
                    }
                )

            user = db.get_or_create_otp_user(
                phone
            )

            token = auth.create_token(
                user["id"],
                user["email"]
            )

            # Record successful OTP login
            try:
                db.record_login(
                    user["id"],
                    "otp"
                )
            except AttributeError:
                pass

            profile = db.get_profile(
                user["id"]
            )

            return json_response(
                self,
                200,
                {
                    "token": token,
                    "user": {
                        "id": user["id"],
                        "name": user["name"],
                        "email": user["email"],
                        "phone": phone,
                    },
                    "profile": profile,
                }
            )

        # ====================================================
        # GOOGLE LOGIN
        # ====================================================

        if path == "/api/auth/google":

            id_token = (
                body.get("id_token")
                or body.get("credential")
                or ""
            ).strip()

            email = (
                body.get("email") or ""
            ).strip().lower()

            name = (
                body.get("name")
                or "User"
            ).strip()

            # Real Google token verification

            if id_token and google_auth:

                verified = (
                    google_auth.verify_google_id_token(
                        id_token
                    )
                )

                if not verified.get("ok"):

                    return json_response(
                        self,
                        401,
                        {
                            "error":
                            verified.get(
                                "error"
                            )
                            or "Invalid Google token"
                        }
                    )

                email = verified["email"].lower()

                name = (
                    verified.get("name")
                    or name
                )

            elif not email:

                return json_response(
                    self,
                    400,
                    {
                        "error":
                        "Google id_token or email required"
                    }
                )

            user = db.get_or_create_google_user(
                email,
                name
            )

            token = auth.create_token(
                user["id"],
                user["email"]
            )

            # Record successful Google login
            try:
                db.record_login(
                    user["id"],
                    "google"
                )
            except AttributeError:
                pass

            profile = db.get_profile(
                user["id"]
            )

            return json_response(
                self,
                200,
                {
                    "token": token,
                    "user": {
                        "id": user["id"],
                        "name": user["name"],
                        "email": user["email"],
                    },
                    "profile": profile,
                }
            )

        # ====================================================
        # AUTHENTICATED USER
        # ====================================================

        user = get_user_from_auth(self)

        # ====================================================
        # REPORT ANALYSIS
        # ====================================================

        if path == "/api/reports/analyze":

            analysis = ai_service.analyze_report(
                body.get("filename")
            )

            report_id = None

            if user:

                report_id = db.save_report(
                    user["id"],
                    body.get("filename")
                    or "upload",
                    analysis
                )

            return json_response(
                self,
                200,
                {
                    "report_id": report_id,
                    "analysis": analysis,
                }
            )

        # ====================================================
        # REPORT TRANSLATION
        # ====================================================

        if path == "/api/reports/translate":

            language = (
                body.get("lang")
                or "en"
            )

            analysis = (
                body.get("analysis")
                or ai_service.DEMO_ANALYSIS
            )

            translated = (
                ai_service.translate_summary(
                    analysis,
                    language
                )
            )

            return json_response(
                self,
                200,
                {
                    "analysis": translated
                }
            )

        # ====================================================
        # CHAT
        # ====================================================

        if path == "/api/chat":

            message = (
                body.get("message")
                or ""
            ).strip()

            language = (
                body.get("language")
                or "en"
            )

            if not message:

                return json_response(
                    self,
                    400,
                    {
                        "error":
                        "Message required"
                    }
                )

            reply = ai_service.chat_reply(
                message,
                language
            )

            if user:

                db.save_chat(
                    user["id"],
                    "user",
                    message
                )

                db.save_chat(
                    user["id"],
                    "bot",
                    reply
                )

            return json_response(
                self,
                200,
                {
                    "reply": reply
                }
            )

        # ====================================================
        # MEDICINE TAKEN
        # ====================================================

        if path == "/api/medicines/taken":

            return json_response(
                self,
                200,
                {
                    "ok": True
                }
            )

        # ====================================================
        # SOS
        # ====================================================

        if path == "/api/sos":

            return json_response(
                self,
                200,
                {
                    "ok": True,
                    "message":
                    "SOS activated. "
                    "Contacts notified (demo).",
                }
            )

        # ====================================================
        # 404
        # ====================================================

        return json_response(
            self,
            404,
            {
                "error":
                "Not found"
            }
        )

    # ========================================================
    # API PUT
    # ========================================================

    def handle_api_put(self, path):

        body = read_json(self)

        user = get_user_from_auth(
            self
        )

        if not user:

            return json_response(
                self,
                401,
                {
                    "error":
                    "Unauthorized"
                }
            )

        # ---------------- PROFILE ----------------

        if path == "/api/profile":

            db.upsert_profile(
                user["id"],
                body
            )

            profile = db.get_profile(
                user["id"]
            )

            return json_response(
                self,
                200,
                {
                    "profile":
                    profile
                }
            )

        return json_response(
            self,
            404,
            {
                "error":
                "Not found"
            }
        )


# ============================================================
# SERVER START
# ============================================================

def main():

    # Initialize database
    db.init_db()

    server = HTTPServer(
        ("0.0.0.0", PORT),
        Handler
    )

    print("=" * 50)
    print("  HealthVerse AI")
    print(
        "  http://localhost:%d"
        % PORT
    )
    print(
        "  Demo: demo@healthverse.ai / demo123"
    )
    print("=" * 50)

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print(
            "\nShutting down..."
        )

        server.server_close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()