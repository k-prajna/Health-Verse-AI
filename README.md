# HealthVerse AI

**Intelligent Healthcare Report Translator & AI Medical Assistant**

Full-stack demo: interactive frontend + Python backend (SQLite + JWT-style tokens).

---

## Color Theme
- Light Purple `#9b7EBD` / `#C9B1E0`
- Light Pink `#F4A6C2` / `#FFD6E5`
- Background `#FDF8FB`

---

## How to Run

### Option 1 — Backend + Frontend together (recommended)

```bash
cd healthverse-ai/backend
python3 main.py
```

Then open your browser:

```
http://localhost:8000
```

The same server serves both the API (`/api/...`) and the static website.

**Windows:** double-click `START.bat`

### Option 2 — Frontend only (offline demo)

Just open `index.html` in a browser.  
All features still work with local simulation (no backend needed).

---

## Demo Login

| Field    | Value                 |
|----------|-----------------------|
| Email    | demo@healthverse.ai   |
| Password | demo123               |

**OTP:** code is shown on screen (or use `123456`)  
**Google:** pick any of the 3 demo accounts

---

## Backend API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Sign up `{name, email, password}` |
| POST | `/api/auth/login` | Login `{email, password}` |
| POST | `/api/auth/otp/send` | Send OTP `{phone}` (returns demo code) |
| POST | `/api/auth/otp/verify` | Verify OTP `{phone, code}` |
| POST | `/api/auth/google` | Simulated Google login |
| GET | `/api/profile` | Get profile (auth required) |
| PUT | `/api/profile` | Update profile |
| POST | `/api/reports/analyze` | Analyze report |
| POST | `/api/reports/translate` | Translate report |
| GET | `/api/reports` | List reports |
| POST | `/api/chat` | AI chat `{message, language}` |
| GET | `/api/chat/history` | Chat history |
| GET | `/api/medicines` | Today's medicines |
| POST | `/api/medicines/taken` | Mark medicine taken |
| GET | `/api/dashboard` | Health dashboard data |
| POST | `/api/sos` | Emergency SOS |

Protected routes need header: `Authorization: Bearer <token>`

---

## Project Structure

```
healthverse-ai/
├── index.html              # Frontend SPA
├── css/styles.css
├── js/app.js               # Frontend logic (backend or offline)
├── backend/
│   ├── main.py             # HTTP server (stdlib) + routes
│   ├── database.py         # SQLite models & queries
│   ├── auth.py             # Token auth + password hashing + OTP
│   ├── ai_service.py       # Mock OCR / analysis / chat / translation
│   ├── data/               # SQLite DB (auto-created)
│   └── uploads/            # Uploaded files
├── START.bat
├── INSTALL.txt
└── README.md
```

---

## Tech Notes

- **No external pip packages required** (Python standard library only).
- Database: **SQLite** (`backend/data/healthverse.db`).
- Auth: signed tokens (72 h) + PBKDF2 password hashes.
- AI features are **simulated** (ready to swap for Gemini / OpenAI / Google Vision).
- Frontend uses the backend when running on port 8000; otherwise falls back to offline mode.

---

## Quick Test

1. Start server: `python3 backend/main.py`
2. Open http://localhost:8000
3. Login with `demo@healthverse.ai` / `demo123`  
   or Sign up / Google / OTP
4. Complete profile
5. Upload a report → see AI analysis + translate
6. Chat with the AI assistant (try language change)
7. Try SOS, medicines, dashboard

---

Built as a production-style demo of the complete HealthVerse AI experience.
