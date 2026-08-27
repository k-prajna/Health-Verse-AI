"""
HealthVerse AI — Configuration
Fill in your real credentials below to enable real Google login and real SMS OTP.
Leave empty to use demo/fallback mode.
"""

# ========== GOOGLE OAUTH ==========
# 1. Go to https://console.cloud.google.com/
# 2. Create a project → APIs & Services → Credentials
# 3. Create OAuth 2.0 Client ID (Web application)
# 4. Authorized JavaScript origins: http://localhost:8000
# 5. Authorized redirect URIs: http://localhost:8000
# 6. Paste Client ID here:
GOOGLE_CLIENT_ID = ""  # e.g. "123456789-xxxx.apps.googleusercontent.com"

# ========== SMS OTP (pick ONE provider) ==========
# Option A: MSG91 (India-friendly) — https://msg91.com
MSG91_AUTH_KEY = ""
MSG91_TEMPLATE_ID = ""  # OTP template ID from MSG91
MSG91_SENDER_ID = "HVAI"  # 6-char sender ID approved by MSG91

# Option B: Twilio — https://www.twilio.com
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_FROM_NUMBER = ""  # e.g. "+1234567890"

# If no SMS keys are set, OTP is shown on screen (demo mode) and 123456 always works.
# Set USE_DEMO_OTP = False only when real SMS is configured.
USE_DEMO_OTP = True

# Server
PORT = 8000
SECRET = "healthverse-demo-secret-change-in-prod"
