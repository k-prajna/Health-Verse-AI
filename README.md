# 🏥 HealthVerse AI

An AI-powered healthcare web application that helps users understand medical reports, receive AI-powered health insights, manage medications, and access emergency assistance through an intuitive interface.

## 🚀 Features

### 🔐 Authentication
- User Registration
- Secure Login
- OTP Verification
- Google Sign-In
- JWT Authentication

### 🤖 AI Healthcare Assistant
- AI-powered medical report analysis
- Health-related chatbot
- Personalized health guidance
- Medical report translation

### 💊 Medicine Management
- Track daily medicines
- Mark medicines as taken
- Medication reminders

### 📄 Medical Reports
- Upload medical reports
- AI analysis of reports
- Translate reports into understandable language
- View report history

### 👤 User Profile
- Update profile information
- Secure authentication
- Personalized dashboard

### 🚨 Emergency Support
- One-click SOS feature
- Quick emergency assistance

---

# 🛠️ Tech Stack

## Frontend
- HTML5
- CSS3
- JavaScript (ES6)

## Backend
- Python
- Python HTTP Server
- SQLite
- JWT Authentication

## AI
- Custom AI Service
- Healthcare Report Analysis

## Deployment
- Frontend: Vercel
- Backend: Render

---

# 📂 Project Structure

```
Health-Verse-AI/
│
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── ai_service.py
│   ├── requirements.txt
│   └── runtime.txt
│
├── css/
│   └── styles.css
│
├── js/
│   └── app.js
│
├── assets/
│
├── index.html
├── README.md
└── START.bat
```

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/k-prajna/Health-Verse-AI.git
cd Health-Verse-AI
```

---

## 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## 3. Run Backend

```bash
python main.py
```

Server starts at:

```
http://localhost:10000
```

---

## 4. Open Application

Open your browser:

```
http://localhost:10000
```

---

# 🌐 Deployment

## Backend (Render)

- Python Runtime
- Root Directory: `backend`
- Start Command:

```bash
python main.py
```

---

## Frontend (Vercel)

Deploy the repository directly on Vercel.

Update `js/app.js` with your Render backend URL:

```javascript
const DEFAULT_API_BASE = "https://your-render-app.onrender.com/api";
```

---

# 📡 API Endpoints

## Authentication

| Method | Endpoint |
|---------|----------|
| POST | `/api/auth/register` |
| POST | `/api/auth/login` |
| POST | `/api/auth/verify-otp` |
| POST | `/api/auth/resend-otp` |
| POST | `/api/auth/google` |

## User

| Method | Endpoint |
|---------|----------|
| GET | `/api/profile` |
| PUT | `/api/profile` |

## AI

| Method | Endpoint |
|---------|----------|
| POST | `/api/chat` |
| GET | `/api/chat/history` |

## Reports

| Method | Endpoint |
|---------|----------|
| POST | `/api/reports/analyze` |
| POST | `/api/reports/translate` |
| GET | `/api/reports` |

## Medicines

| Method | Endpoint |
|---------|----------|
| GET | `/api/medicines` |
| POST | `/api/medicines/taken` |

## Emergency

| Method | Endpoint |
|---------|----------|
| POST | `/api/sos` |

---

# ✨ Future Improvements

- Voice-enabled AI assistant
- Doctor appointment booking
- OCR for medical reports
- Health analytics dashboard
- Multi-language support
- AI symptom checker
- Cloud database integration

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push to your branch

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# 📜 License

This project is licensed under the MIT License.

---

# 👩‍💻 Author

**Prajna K**

- GitHub: https://github.com/k-prajna

---

⭐ If you found this project useful, consider giving it a **Star** on GitHub!
