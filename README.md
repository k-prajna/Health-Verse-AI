# HealthVerse AI (Latest)

## What's new
- **Real Google OAuth** via Google Identity Services (set your Client ID)
- Stethoscope icon (splash, header, login)
- Animated girl character on login (walks in, dances on success)
- Profile page with 4 tabs: Personal | Locker | Alerts | Settings
- Tulu language (text fully works; voice falls back with a clear message)
- Demo Google accounts still work when Client ID is empty

## How to run

### With backend (recommended)
```bash
cd healthverse-ai/backend
python main.py
```
Open http://localhost:8000

### Frontend only
```bash
cd healthverse-ai
python -m http.server 8080
```
Open http://localhost:8080

Camera, mic, and notifications need http:// — do not open index.html by double-click.

---

## Enable REAL Google Sign-In (5 minutes)

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select one)
3. Go to **APIs & Services → Credentials**
4. Click **+ CREATE CREDENTIALS → OAuth client ID**
5. Application type: **Web application**
6. Name it e.g. `HealthVerse Local`
7. **Authorized JavaScript origins**:
   - `http://localhost:8000`
   - `http://localhost:8080`
8. **Authorized redirect URIs** (same):
   - `http://localhost:8000`
   - `http://localhost:8080`
9. Click Create → copy the **Client ID** (looks like `123456789-xxxx.apps.googleusercontent.com`)

10. Paste the Client ID in **two places**:
    - `js/app.js` → line near the top: `const GOOGLE_CLIENT_ID = "YOUR_ID_HERE";`
    - `backend/auth.py` → `GOOGLE_CLIENT_ID = "YOUR_ID_HERE"`

11. Restart the backend (`python main.py`) and refresh the browser.

You will now see the official Google account picker with your real Google accounts.

> Leave `GOOGLE_CLIENT_ID = ""` (empty) to keep the 3 demo accounts working.

---

## Other production TODOs
- Real OTP SMS → Twilio / MSG91 / AWS SNS
- Translation/AI → Google Gemini / OpenAI
- OCR → Google Vision API or Tesseract
