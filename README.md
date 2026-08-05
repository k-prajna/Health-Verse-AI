# HealthVerse AI

HealthVerse AI is a healthcare-focused web application that combines medical report understanding, personalized health insights, secure authentication, and AI-powered assistance.

The project currently uses a Python backend with an SQLite database and supports secure email/password login followed by email OTP verification.

## Overview

HealthVerse AI helps users manage health-related information through a modern web interface. The app includes:

- user registration and login
- password-based authentication with email OTP verification
- profile management
- dashboard and health insights
- report upload and analysis workflow
- medicine reminders and tracking
- AI-style healthcare assistant experience

## Authentication Flow

The current login process is:

1. Register with full name, email, and password
2. Login with email and password
3. If the password is correct, generate a 6-digit OTP
4. Send the OTP to the registered email
5. Verify the OTP to complete login

This means the app uses both password authentication and OTP verification for security.

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python
- Web server: Python HTTP server
- Database: SQLite
- Authentication: password hashing, JWT-style tokens, email OTP

## Database

The application currently uses SQLite for local development.

Database file:
- backend/data/healthverse.db

The database stores:
- users
- profiles
- reports
- medicines
- chat history
- OTP verification records
- sessions

## Project Structure

- index.html — main frontend page
- css/styles.css — UI styling
- js/app.js — frontend logic, navigation, and auth flow
- backend/main.py — backend server and API routes
- backend/auth.py — password hashing, JWT, OTP, and email helpers
- backend/database.py — SQLite database layer
- backend/data/healthverse.db — local database file

## How to Run

### 1. Start the backend
```bash
cd backend
python main.py
```
Then open:
- http://localhost:8000

### 2. Start the frontend (optional, if serving separately)
```bash
cd ..
python -m http.server 8080
```
Then open:
- http://localhost:8080

> For the best experience, run the backend so the frontend can communicate with the API correctly.

## API Endpoints

The backend currently supports these auth endpoints:

- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/verify-otp
- POST /api/auth/resend-otp
- POST /api/auth/logout
- GET /api/auth/me
- POST /api/auth/forgot-password
- POST /api/auth/reset-password

## Environment Variables

For real email delivery, set the following values before starting the backend:

```bash
SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=
JWT_SECRET=
```

## Notes

- Passwords are stored as salted hashes.
- OTPs are hashed before storage.
- The current setup is intended for local development and testing.
- No API key is required for the current authentication flow.
