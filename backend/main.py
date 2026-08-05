#!/usr/bin/env python3
"""
HealthVerse AI - Backend Server
Pure Python (stdlib + PyJWT). Serves REST API + static frontend.

Usage:
    python3 main.py
    # then open http://localhost:8000
"""
import json
import mimetypes
import os
import socket
import sys
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

# Local modules
sys.path.insert(0, str(Path(__file__).parent))
import database as db
import auth
import ai_service

# Config
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 10000))
BACKEND_DIR = Path(__file__).parent.resolve()
FRONTEND_DIR = BACKEND_DIR.parent  # healthverse-ai/
DATA_DIR = BACKEND_DIR / "data"
UPLOAD_DIR = BACKEND_DIR / "uploads"
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Max body size 10 MB
MAX_BODY = 10 * 1024 * 1024

class DualStackHTTPServer(HTTPServer):
    address_family = socket.AF_INET6

    def server_bind(self):
        # On Windows, binding AF_INET6 to the IPv4 wildcard address 0.0.0.0 fails.
        # For all-interface binding, use the IPv6 wildcard :: and allow dual-stack.
        bind_address = self.server_address
        if bind_address[0] == "0.0.0.0":
            bind_address = ("::", bind_address[1], 0, 0)

        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except OSError:
            pass

        self.socket.bind(bind_address)
        self.server_address = bind_address


class HealthVerseHandler(BaseHTTPRequestHandler):
    server_version = "HealthVerseAI/1.0"

    # Helpers
    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _json_response(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._set_cors()
        self.end_headers()
        self.wfile.write(body)

    def _error(self, message, status=400):
        self._json_response({"ok": False, "error": message}, status)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_BODY:
            raise ValueError("Body too large")
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {"_raw": raw}

    def _get_user(self):
        """Extract user from Authorization: Bearer <token>"""
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None
        token = header[7:].strip()
        payload = auth.decode_token(token)
        if not payload:
            return None
        uid = payload.get("sub")
        if not uid:
            return None
        return db.get_user_by_id(uid)

    def _require_auth(self):
        user = self._get_user()
        if not user:
            self._error("Unauthorized. Please login.", 401)
            return None
        return user

    # Routing
    def do_OPTIONS(self):
        print(f"[Request] OPTIONS {self.path} from {self.client_address[0]}")
        self.send_response(204)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        print(f"[Request] GET {self.path} from {self.client_address[0]}")
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        # API routes
        if path.startswith("/api/"):
            self._handle_api_get(path, parse_qs(parsed.query))
            return

        # Static files
        self._serve_static(path)

    def do_HEAD(self):
        print(f"[Request] HEAD {self.path} from {self.client_address[0]}")
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path.startswith("/api/"):
            # Most browsers only need HEAD for resource checks. Return headers only.
            self.send_response(200)
            self._set_cors()
            self.end_headers()
            return

        if path == "/":
            path = "/index.html"

        file_path = (FRONTEND_DIR / path.lstrip("/")).resolve()
        if not str(file_path).startswith(str(FRONTEND_DIR.resolve())):
            self.send_error(403)
            return
        if not file_path.is_file():
            self.send_error(404)
            return

        content_type, _ = mimetypes.guess_type(str(file_path))
        content_type = content_type or "application/octet-stream"
        file_size = file_path.stat().st_size

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(file_size))
        self._set_cors()
        self.end_headers()

    def do_POST(self):
        print(f"[Request] POST {self.path} from {self.client_address[0]}")
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        if not path.startswith("/api/"):
            self._error("Not found", 404)
            return
        try:
            body = self._read_body()
        except ValueError as e:
            self._error(str(e), 413)
            return
        self._handle_api_post(path, body)

    def do_PUT(self):
        print(f"[Request] PUT {self.path} from {self.client_address[0]}")
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        if not path.startswith("/api/"):
            self._error("Not found", 404)
            return
        try:
            body = self._read_body()
        except ValueError as e:
            self._error(str(e), 413)
            return
        self._handle_api_put(path, body)

    # API GET
    def _handle_api_get(self, path, query):
        try:
            if path == "/api/health":
                self._json_response({"ok": True, "service": "HealthVerse AI", "version": "1.0"})
                return

            if path == "/api/profile":
                user = self._require_auth()
                if not user:
                    return
                profile = db.get_profile(user["id"])
                self._json_response({"ok": True, "profile": profile})
                return

            if path == "/api/reports":
                user = self._require_auth()
                if not user:
                    return
                reports = db.get_reports(user["id"])
                self._json_response({"ok": True, "reports": reports})
                return

            if path.startswith("/api/reports/"):
                user = self._require_auth()
                if not user:
                    return
                try:
                    rid = int(path.split("/")[-1])
                except ValueError:
                    self._error("Invalid report id")
                    return
                report = db.get_report(user["id"], rid)
                if not report:
                    self._error("Report not found", 404)
                    return
                self._json_response({"ok": True, "report": report})
                return

            if path == "/api/medicines":
                user = self._require_auth()
                if not user:
                    return
                meds = db.get_medicines(user["id"])
                self._json_response({"ok": True, "medicines": meds})
                return

            if path == "/api/dashboard":
                user = self._require_auth()
                if not user:
                    return
                data = db.get_dashboard(user["id"])
                profile = db.get_profile(user["id"])
                score = ai_service.generate_health_score(profile, data.get("metrics", {}))
                data["health_score"] = score
                self._json_response({"ok": True, "dashboard": data})
                return

            if path == "/api/chat/history":
                user = self._require_auth()
                if not user:
                    return
                history = db.get_chat_history(user["id"])
                self._json_response({"ok": True, "messages": history})
                return

            self._error("Endpoint not found", 404)
        except Exception as e:
            traceback.print_exc()
            self._error(f"Server error: {e}", 500)

    # API POST
    def _handle_api_post(self, path, body):
        try:
            # Auth
            if path == "/api/auth/register":
                name = (body.get("name") or "").strip()
                email = (body.get("email") or "").strip().lower()
                password = body.get("password") or ""
                confirm_password = body.get("confirm_password") or ""
                if not name or not email or not password:
                    self._error("name, email and password are required")
                    return
                if not auth.is_valid_email(email):
                    self._error("Please enter a valid email address")
                    return
                if password != confirm_password:
                    self._error("Passwords do not match")
                    return
                if not auth.is_strong_password(password):
                    self._error("Password must be at least 8 characters, include uppercase, lowercase, number, and a symbol")
                    return
                if db.get_user_by_email(email):
                    self._error("This email is already registered. Please log in using your existing account.", 409)
                    return
                pw_hash = auth.hash_password(password)
                uid = db.create_user(name=name, email=email, password_hash=pw_hash)
                token = auth.create_token(uid, name, email)
                self._json_response({
                    "ok": True,
                    "status": "SUCCESS",
                    "token": token,
                    "user": {"id": uid, "name": name, "email": email}
                }, 201)
                return

            if path == "/api/auth/login":
                email = (body.get("email") or "").strip().lower()
                password = body.get("password") or ""
                if not auth.is_valid_email(email):
                    self._error("Please enter a valid email address")
                    return
                user = db.get_user_by_email(email)
                if not user or not user.get("password_hash"):
                    self._error("Invalid email or password", 401)
                    return
                if not auth.verify_password(password, user["password_hash"]):
                    self._error("Invalid email or password", 401)
                    return
                otp_code = auth.generate_otp_code()
                otp_hash = auth.hash_otp(otp_code)
                expires_at = (datetime.utcnow() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
                db.save_otp(user["id"], otp_hash, expires_at)
                auth.send_otp_email(user.get("email"), otp_code)
                self._json_response({
                    "ok": True,
                    "status": "OTP_REQUIRED",
                    "message": "Verification code sent to your registered email.",
                    "user": {"id": user["id"], "name": user["name"], "email": user.get("email")}
                })
                return

            if path == "/api/auth/verify-otp":
                email = (body.get("email") or "").strip().lower()
                code = (body.get("code") or "").strip()
                if not email or not code:
                    self._error("email and code are required")
                    return
                user = db.get_user_by_email(email)
                if not user:
                    self._error("Invalid email or password", 401)
                    return
                otp = db.get_active_otp(user["id"])
                if not otp:
                    self._error("Your verification code has expired. Please request a new code.", 401)
                    return
                if int(otp.get("attempts", 0)) >= auth.OTP_MAX_ATTEMPTS:
                    self._error("Too many incorrect attempts. Please request a new verification code.", 401)
                    return
                if datetime.utcnow() > datetime.strptime(otp["expires_at"], "%Y-%m-%d %H:%M:%S"):
                    self._error("Your verification code has expired. Please request a new code.", 401)
                    return
                if not auth.verify_otp_code(code, otp["otp_hash"]):
                    db.increment_otp_attempts(otp["id"])
                    self._error("Invalid verification code. Please try again.", 401)
                    return
                db.mark_otp_used(otp["id"])
                token = auth.create_token(user["id"], user["name"], user.get("email"))
                expires_at = (datetime.utcnow() + timedelta(hours=auth.JWT_EXPIRE_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
                db.create_session(user["id"], token, expires_at)
                profile = db.get_profile(user["id"])
                self._json_response({
                    "ok": True,
                    "status": "SUCCESS",
                    "access_token": token,
                    "token_type": "bearer",
                    "user": {
                        "id": user["id"],
                        "name": user["name"],
                        "email": user.get("email"),
                        "profile_complete": bool(profile and profile.get("age"))
                    }
                })
                return

            if path == "/api/auth/resend-otp":
                email = (body.get("email") or "").strip().lower()
                if not email:
                    self._error("email is required")
                    return
                if not auth.is_valid_email(email):
                    self._error("Please enter a valid email address")
                    return
                if not auth.can_resend_otp(email):
                    self._error("Resend available in 30 seconds.", 429)
                    return
                user = db.get_user_by_email(email)
                if not user:
                    self._error("Invalid email or password", 401)
                    return
                otp_code = auth.generate_otp_code()
                otp_hash = auth.hash_otp(otp_code)
                expires_at = (datetime.utcnow() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
                db.save_otp(user["id"], otp_hash, expires_at)
                auth.record_otp_resend(email)
                auth.send_otp_email(user.get("email"), otp_code)
                self._json_response({"ok": True, "status": "OTP_REQUIRED", "message": "Verification code sent to your registered email."})
                return

            if path == "/api/auth/logout":
                user = self._require_auth()
                if not user:
                    return
                db.invalidate_sessions(user["id"])
                self._json_response({"ok": True, "message": "Logged out successfully"})
                return

            if path == "/api/auth/me":
                user = self._require_auth()
                if not user:
                    return
                profile = db.get_profile(user["id"])
                self._json_response({"ok": True, "user": {"id": user["id"], "name": user["name"], "email": user.get("email"), "profile_complete": bool(profile and profile.get("age"))}})
                return

            if path == "/api/auth/forgot-password":
                email = (body.get("email") or "").strip().lower()
                if not email:
                    self._error("email is required")
                    return
                user = db.get_user_by_email(email)
                if not user:
                    self._error("Invalid email or password", 401)
                    return
                self._json_response({"ok": True, "message": "Password reset instructions sent to your email"})
                return

            if path == "/api/auth/reset-password":
                email = (body.get("email") or "").strip().lower()
                password = body.get("password") or ""
                if not email or not password:
                    self._error("email and password are required")
                    return
                user = db.get_user_by_email(email)
                if not user:
                    self._error("Invalid email or password", 401)
                    return
                if not auth.is_strong_password(password):
                    self._error("Password must be at least 8 characters, include uppercase, lowercase, number, and a symbol")
                    return
                db.update_user_password(user["id"], auth.hash_password(password))
                db.invalidate_sessions(user["id"])
                self._json_response({"ok": True, "message": "Password updated successfully"})
                return

            if path == "/api/auth/google":
                # Real Google OAuth: prefer ID token (credential) from GIS
                # Fallback: accept name/email for demo accounts when Client ID not set
                credential = (body.get("credential") or body.get("id_token") or "").strip()
                name = (body.get("name") or "").strip()
                email = (body.get("email") or "").strip().lower()

                if credential:
                    payload = auth.verify_google_id_token(credential)
                    if not payload or not payload.get("email"):
                        self._error("Invalid or expired Google ID token", 401)
                        return
                    email = payload["email"].lower()
                    name = payload.get("name") or email.split("@")[0]
                elif not email:
                    self._error("Google credential or email required", 400)
                    return
                else:
                    # Demo path (no real token) — only allowed when GOOGLE_CLIENT_ID is empty
                    if auth.GOOGLE_CLIENT_ID:
                        self._error("Real Google Sign-In required. Configure GOOGLE_CLIENT_ID.", 401)
                        return
                    name = name or "Google User"

                user = db.get_user_by_email(email)
                if not user:
                    uid = db.create_user(name=name, email=email)
                    user = db.get_user_by_id(uid)
                token = auth.create_token(user["id"], user["name"], email)
                profile = db.get_profile(user["id"])
                self._json_response({
                    "ok": True,
                    "token": token,
                    "user": {
                        "id": user["id"],
                        "name": user["name"],
                        "email": email,
                        "profile_complete": bool(profile and profile.get("age"))
                    }
                })
                return

            # Report upload & analysis
            if path == "/api/reports/analyze":
                user = self._require_auth()
                if not user:
                    return
                filename = body.get("filename") or "report.pdf"
                raw_text = body.get("text") or ""
                analysis = ai_service.analyze_report(filename, raw_text)
                rid = db.save_report(
                    user["id"],
                    filename,
                    raw_text,
                    analysis,
                    analysis.get("risk_level", "moderate")
                )
                self._json_response({
                    "ok": True,
                    "report_id": rid,
                    "analysis": analysis
                })
                return

            if path == "/api/reports/translate":
                user = self._require_auth()
                if not user:
                    return
                rid = body.get("report_id")
                lang = body.get("lang") or "en"
                if not rid:
                    self._error("report_id required")
                    return
                report = db.get_report(user["id"], int(rid))
                if not report:
                    self._error("Report not found", 404)
                    return
                analysis = report.get("analysis") or {}
                translated = ai_service.translate_analysis(analysis, lang)
                db.save_translation(int(rid), lang, translated.get("summary", ""))
                self._json_response({"ok": True, "translation": translated})
                return

            # Chat
            if path == "/api/chat":
                user = self._require_auth()
                if not user:
                    return
                message = (body.get("message") or "").strip()
                if not message:
                    self._error("message is required")
                    return
                db.save_chat(user["id"], "user", message)
                history = db.get_chat_history(user["id"], limit=10)
                reply = ai_service.chat_reply(message, history)
                db.save_chat(user["id"], "assistant", reply)
                self._json_response({"ok": True, "reply": reply})
                return

            # Medicine taken
            if path == "/api/medicines/taken":
                user = self._require_auth()
                if not user:
                    return
                med_id = body.get("medicine_id")
                taken = body.get("taken", True)
                if not med_id:
                    self._error("medicine_id required")
                    return
                db.mark_medicine_taken(user["id"], int(med_id), taken)
                self._json_response({"ok": True})
                return

            # SOS
            if path == "/api/sos":
                user = self._require_auth()
                if not user:
                    return
                profile = db.get_profile(user["id"])
                # In production: notify contacts, share location, alert hospitals
                self._json_response({
                    "ok": True,
                    "message": "SOS activated",
                    "shared": {
                        "name": profile.get("name"),
                        "blood_group": profile.get("blood_group"),
                        "allergies": profile.get("allergies"),
                        "emergency_contact": profile.get("emergency_contact"),
                        "medicines": [m["name"] for m in db.get_medicines(user["id"])]
                    }
                })
                return

            self._error("Endpoint not found", 404)
        except Exception as e:
            traceback.print_exc()
            self._error(f"Server error: {e}", 500)

    # API PUT
    def _handle_api_put(self, path, body):
        try:
            if path == "/api/profile":
                user = self._require_auth()
                if not user:
                    return
                # Map frontend keys ΓåÆ DB columns
                mapping = {
                    "name": "name",
                    "age": "age",
                    "gender": "gender",
                    "blood": "blood_group",
                    "blood_group": "blood_group",
                    "height": "height_cm",
                    "height_cm": "height_cm",
                    "weight": "weight_kg",
                    "weight_kg": "weight_kg",
                    "allergies": "allergies",
                    "diseases": "diseases",
                    "emergency": "emergency_contact",
                    "emergency_contact": "emergency_contact",
                    "language": "preferred_language",
                    "preferred_language": "preferred_language",
                }
                data = {}
                for k, v in body.items():
                    if k in mapping and v is not None and v != "":
                        data[mapping[k]] = v
                db.update_profile(user["id"], data)
                profile = db.get_profile(user["id"])
                self._json_response({"ok": True, "profile": profile})
                return

            self._error("Endpoint not found", 404)
        except Exception as e:
            traceback.print_exc()
            self._error(f"Server error: {e}", 500)

    # Static file server
    def _serve_static(self, path):
        if path == "/":
            path = "/index.html"
        # Security: prevent path traversal
        file_path = (FRONTEND_DIR / path.lstrip("/")).resolve()
        if not str(file_path).startswith(str(FRONTEND_DIR.resolve())):
            self.send_error(403)
            return
        if not file_path.is_file():
            self.send_error(404)
            return
        content_type, _ = mimetypes.guess_type(str(file_path))
        content_type = content_type or "application/octet-stream"
        try:
            data = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self._set_cors()
            self.end_headers()
            self.wfile.write(data)
        except Exception:
            self.send_error(500)

    def log_message(self, format, *args):
        print(f"[HTTP] {self.address_string()} - {format % args}")


def main():
    print("=" * 55)
    print("  HealthVerse AI — Backend Server")
    print("=" * 55)
    print(f"[Server] Working dir  : {Path.cwd()}")
    print(f"[Server] Backend dir  : {BACKEND_DIR}")
    print(f"[Server] Frontend dir : {FRONTEND_DIR}")
    print(f"[Server] Index exists : { (FRONTEND_DIR / 'index.html').is_file() }")
    print(f"[Server] Database path: {db.DB_PATH}")
    print(f"[Server] PORT         : {PORT}")

    try:
        db.init_db()
        print(f"[Server] Listening on  http://{HOST}:{PORT}")
        print(f"[Server] Browser URLs  http://127.0.0.1:{PORT} and http://localhost:{PORT}")
        print(f"[Server] API base      http://0.0.0.0:{PORT}/api/")
        if (FRONTEND_DIR / 'index.html').is_file():
            print(f"[Server] Serving index file from {(FRONTEND_DIR / 'index.html')}")
        else:
            print("[WARNING] index.html not found at frontend root")
        print("  Press Ctrl+C to stop")
        print("=" * 55)

        server = DualStackHTTPServer((HOST, PORT), HealthVerseHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[Server] Shutting down...")
            server.shutdown()
        except Exception as e:
            print(f"[ERROR] Server runtime error: {e}")
            traceback.print_exc()
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Startup failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

