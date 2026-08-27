# Real Google + Real Phone OTP Setup

By default the app runs in **demo mode** (no API keys needed).
To use **your real Gmail** and **real phone SMS OTP**, follow the steps below.

---

## 1. Real Google (Gmail) Sign-In

### Create OAuth Client ID
1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select one)
3. Go to **APIs & Services → OAuth consent screen**
   - User type: External
   - App name: HealthVerse AI
   - Add your email as test user
4. Go to **Credentials → Create Credentials → OAuth client ID**
   - Application type: **Web application**
   - Name: HealthVerse Web
   - **Authorized JavaScript origins:**
     - `http://localhost:8000`
     - `http://127.0.0.1:8000`
   - **Authorized redirect URIs:**
     - `http://localhost:8000`
     - `http://127.0.0.1:8000`
5. Copy the **Client ID** (ends with `.apps.googleusercontent.com`)

### Put Client ID in config
Edit `backend/config.py`:

```python
GOOGLE_CLIENT_ID = "YOUR_CLIENT_ID.apps.googleusercontent.com"
```

Restart the server (`python main.py`), open http://localhost:8000  
Click **Google** → choose your **real Gmail account** → signed in.

The server verifies the Google ID token with Google’s servers (not a dummy list).

---

## 2. Real Phone OTP (SMS)

Pick **one** provider.

### Option A — MSG91 (good for India)
1. Sign up at https://msg91.com  
2. Get **Auth Key** and create an **OTP / Flow template**  
3. In `backend/config.py`:

```python
MSG91_AUTH_KEY = "your_auth_key"
MSG91_TEMPLATE_ID = "your_template_id"
MSG91_SENDER_ID = "HVAI"   # must be approved
USE_DEMO_OTP = False
```

### Option B — Twilio (global)
1. Sign up at https://www.twilio.com  
2. Get Account SID, Auth Token, and a From number  
3. In `backend/config.py`:

```python
TWILIO_ACCOUNT_SID = "ACxxxxxxxx"
TWILIO_AUTH_TOKEN = "your_token"
TWILIO_FROM_NUMBER = "+1234567890"
USE_DEMO_OTP = False
```

Restart the server. Enter a **real phone number** (+91… or full international).  
OTP is sent by SMS — **not** shown on screen.

Until keys are set, OTP stays in demo mode (code on screen + `123456`).

---

## Security notes
- Never commit real API keys to public git
- Change `SECRET` in `config.py` for production
- Use HTTPS in production (Google requires HTTPS except localhost)

---

## Quick check
```bash
cd backend
python3 main.py
# Visit http://localhost:8000/api/health
# Should show "google_client_id" and "real_sms": true when configured
```
