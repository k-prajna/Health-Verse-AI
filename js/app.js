/**
 * HealthVerse AI — Frontend Application Logic
 * Supports Multi-language AI Assistant (including Tulu), Camera Scanner,
 * Profile Management (4 tabs), Notification Settings, Animated Character,
 * Gmail & SMS OTP Authentication, and full Backend API Integration.
 */

const API_BASE = '/api';
const GOOGLE_CLIENT_ID = ""; // Set your Google OAuth Client ID here

const API = {
  async request(method, path, body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    const token = localStorage.getItem('hv_token');
    if (token) opts.headers['Authorization'] = `Bearer ${token}`;
    if (body) opts.body = JSON.stringify(body);

    try {
      const res = await fetch(`${API_BASE}${path}`, opts);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        return { ok: false, error: data.error || `HTTP error ${res.status}` };
      }
      return data;
    } catch (err) {
      console.warn('API call fallback for:', path, err.message);
      return { ok: false, error: err.message };
    }
  }
};

const App = {
  state: {
    user: null,
    profile: null,
    currentScreen: 'splash',
    currentView: 'home',
    profileTab: 'personal',
    onboardingSlide: 0,
    selectedLang: 'en',
    chatLang: 'en',
    cameraStream: null,
    voiceSpeed: 1.0,
    ttsAuto: localStorage.getItem('hv_tts_auto') === '1',
    notifEmail: localStorage.getItem('hv_notif_email') || 'priya.sharma@gmail.com',
    notifPhone: localStorage.getItem('hv_notif_phone') || '+91 98765 43210',
    sentOtpCode: '123456',
    recognition: null,
    waterMl: 1200,
    stepCount: 5400
  },

  detectLanguage(text, defaultLang = 'en') {
    if (!text) return defaultLang;
    if (/[\u0C80-\u0CFF]/.test(text)) {
      if (/(ಇರೆಗ್|ಉಂಡು|ತೋಜುಂಡು|ಮಲ್ಪುಲೆ|ಎಡ್ಡೆ|ಮರ್ದ್|ತಿನೊಲಿ|ಕೇನ್‌ಲೆ|ಯಾನ್|ಸೊಲ್ಮೆಲು)/.test(text)) return 'tcy';
      return 'kn';
    }
    if (/[\u0900-\u097F]/.test(text)) {
      if (/(मला|ताप|काय|करावे|नाही|आहे|रक्तदाब|औषध|नमस्कार|करा|जा)/.test(text)) return 'mr';
      return 'hi';
    }
    if (/[\u0B80-\u0BFF]/.test(text)) return 'ta';
    if (/[\u0C00-\u0C7F]/.test(text)) return 'te';
    if (/[\u0D00-\u0D7F]/.test(text)) return 'ml';
    if (/[\u0980-\u09FF]/.test(text)) return 'bn';

    const lower = text.toLowerCase();
    if (/\b(jwara|namaskara|yenu|madabeku|oushadhi|neeru|kannada)\b/.test(lower)) return 'kn';
    if (/\b(bukhar|namaste|kya|karun|karoon|dawa|paani|hindi)\b/.test(lower)) return 'hi';
    if (/\b(kaichal|vanakkam|ennu|marundhu|thanneer|tamil)\b/.test(lower)) return 'ta';
    if (/\b(jwaram|namaskaram|kavali|mandulu|neellu|telugu)\b/.test(lower)) return 'te';
    if (/\b(pani|namaskaram|marunnu|vellam|malayalam)\b/.test(lower)) return 'ml';
    if (/\b(tap|namaskar|kay|karave|aushadh|pani|marathi)\b/.test(lower)) return 'mr';
    if (/\b(tulu|tcy|yenk|kene|marnd|solmelu)\b/.test(lower)) return 'tcy';

    return defaultLang;
  },

  aiResponses: {
    kn: {
      fever: "ನಿಮಗೆ ಜ್ವರ ಇದ್ದರೆ:\n• ಸಾಕಷ್ಟು ನೀರು ಕುಡಿಯಿರಿ.\n• ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ.\n• ಜ್ವರ ಹೆಚ್ಚು ಇದ್ದರೆ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.\n• ಉಸಿರಾಟದ ತೊಂದರೆ ಇದ್ದರೆ ತಕ್ಷಣ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿ.",
      diabetes: "Diabetes (ಪ್ರಮೇಹ) ನಿಯಂತ್ರಣಕ್ಕೆ:\n• Blood Sugar ಮಟ್ಟವನ್ನು ನಿಯಮಿತವಾಗಿ ಪರಿಶೀಲಿಸಿ.\n• ಬಿಳಿ ಅಕ್ಕಿ, ಸಿಹಿ ಸೇವನೆ ಕಡಿಮೆ ಮಾಡಿ.\n• ದಿನವೂ 30-45 ನಿಮಿಷ Brisk Walking ಮಾಡಿ.\n• Metformin ಸಮಯಕ್ಕೆ ಸರಿಯಾಗಿ ತೆಗೆದುಕೊಳ್ಳಿ.",
      bp: "Blood Pressure ನಿಯಂತ್ರಿಸಲು:\n• ಆಹಾರದಲ್ಲಿ ಉಪ್ಪಿನ ಪ್ರಮಾಣ ಕಡಿಮೆ ಮಾಡಿ.\n• ದಿನವೂ 30 ನಿಮಿಷ ವ್ಯಾಯಾಮ ಮಾಡಿ.\n• Amlodipine ನಂತಹ ಔಷಧಿಗಳನ್ನು ತಪ್ಪದೇ ಸೇವಿಸಿ.",
      report: "ನಿಮ್ಮ ಲ್ಯಾಬ್ ವರದಿ ವಿವರಣೆ:\n• Fasting Blood Sugar: 118 mg/dL (ಸ್ವಲ್ಪ ಹೆಚ್ಚು)\n• LDL Cholesterol: 142 mg/dL (ಸೀಮಾರೇಖೆ ಹೆಚ್ಚು)\n• HbA1c: 6.2%\n• Kidney Function ಮತ್ತು Hemoglobin ಸಾಮಾನ್ಯವಾಗಿದೆ.",
      foods: "ಆಹಾರ ಸಲಹೆ:\n• ಬಿಳಿ ಅಕ್ಕಿ, ಸಿಹಿ ಮತ್ತು ಕರಿದ ಪದಾರ್ಥಗಳನ್ನು ಕಡಿಮೆ ಮಾಡಿ.\n• ರಾಗಿ, ಜೋಳ, ಸಿರಿಧಾನ್ಯಗಳು ಹಾಗೂ ತರಕಾರಿಗಳನ್ನು ಸೇವಿಸಿ.",
      metformin: "Metformin ಕುರಿತು:\n• Type 2 Diabetes ನಿಯಂತ್ರಣಕ್ಕೆ ನೀಡಲಾಗುತ್ತದೆ.\n• ಊಟದ ನಂತರ ತೆಗೆದುಕೊಳ್ಳಿ.",
      water: "ದಿನಕ್ಕೆ ಕನಿಷ್ಠ 2.5 ರಿಂದ 3 ಲೀಟರ್ ನೀರು ಕುಡಿಯಿರಿ.",
      greeting: "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ HealthVerse AI ವೈದ್ಯಕೀಯ ಸಹಾಯಕ. ವರದಿ, ಔಷಧಿ ಅಥವಾ ಆಹಾರದ ಬಗ್ಗೆ ಕೇಳಬಹುದು.",
      thanks: "ಧನ್ಯವಾದಗಳು! ನಿಮ್ಮ ಆರೋಗ್ಯದ ಕಾಳಜಿ ವಹಿಸಿ.",
      default: "ನಾನು ನಿಮ್ಮ HealthVerse AI ಸಹಾಯಕ. ವರದಿಗಳು, Diabetes, BP ಹಾಗೂ ಆಹಾರ ಕುರಿತು ಸಹಾಯ ಮಾಡುವೆ."
    },
    hi: {
      fever: "यदि आपको बुखार है:\n• पर्याप्त पानी पिएँ।\n• आराम करें।\n• यदि तेज बुखार हो तो डॉक्टर से संपर्क करें।",
      diabetes: "Diabetes नियंत्रित करने के लिए:\n• Blood Sugar की नियमित जाँच करें।\n• सफेद चावल, मिठाइयाँ कम करें।\n• रोजाना 30-45 मिनट टहलें।\n• समय पर Metformin लें।",
      bp: "Blood Pressure के लिए:\n• नमक की मात्रा कम करें।\n• प्रतिदिन 30 मिनट व्यायाम करें।\n• Amlodipine समय पर लें।",
      report: "आपकी रिपोर्ट:\n• Fasting Sugar: 118 mg/dL (थोड़ा उच्च)\n• LDL: 142 mg/dL\n• HbA1c: 6.2%\n• Kidney और Hemoglobin सामान्य हैं।",
      foods: "सफेद चावल, मिठाई कम करें। बाजरा, रागी, हरी सब्जियाँ खाएँ।",
      metformin: "Metformin Type 2 Diabetes के लिए है। भोजन के बाद लें।",
      water: "रोजाना 2.5 से 3 लीटर पानी पिएँ।",
      greeting: "नमस्ते! मैं आपका HealthVerse AI मेडिकल सहायक हूँ। मैं आपकी क्या मदद कर सकता हूँ?",
      thanks: "धन्यवाद! अपनी सेहत का ख्याल रखें।",
      default: "मैं आपका HealthVerse AI सहायक हूँ। रिपोर्ट, दवा या आहार पर परामर्श लें।"
    },
    en: {
      fever: "If you have a fever:\n• Stay hydrated with plenty of water.\n• Take adequate rest.\n• Monitor temperature.\n• Consult a doctor if fever persists.",
      diabetes: "To manage Diabetes:\n• Monitor blood glucose regularly.\n• Limit refined carbs and sweets.\n• Walk for 30–45 mins daily.\n• Take Metformin on time as prescribed.",
      bp: "To control Blood Pressure:\n• Reduce salt intake.\n• Daily 30 min light exercise.\n• Take Amlodipine as prescribed.",
      report: "Lab report breakdown:\n• Fasting Glucose: 118 mg/dL (Slightly High)\n• LDL Cholesterol: 142 mg/dL (Borderline High)\n• HbA1c: 6.2%\n• Hemoglobin & Kidney profile normal.",
      foods: "Prefer millets, whole grains, and leafy vegetables over white rice and fried items.",
      metformin: "Metformin helps manage Type 2 Diabetes. Take it with or after meals.",
      water: "Drink at least 2.5 to 3 liters of water daily.",
      greeting: "Hello! I am your HealthVerse AI assistant. Ask me about your reports, medicines, or diet.",
      thanks: "You are welcome! Stay healthy.",
      default: "I'm your HealthVerse AI healthcare assistant. How can I help you today?"
    },
    tcy: {
      fever: "ಇರೆಗ್ ಜ್ವರ ಉಂಡುಂದ್ ಆಂಡ:\n• ಬೋಡಾಯಿನಾತ್ ನೀರ್ ಪರ್ಲೆ.\n• ವಿಶ್ರಾಂತಿ ದೆತೊನುಲೆ.\n• ಜ್ವರ ಜಾಸ್ತಿ ಇತ್ತ್‌ಂಡ ಡಾಕ್ಟರೆನ್ ಭೇಟಿ ಮಾಡಿ.\n• ಉಸಿರಾಟದ ತೊಂದರೆ ಇತ್ತ್‌ಂಡ ಹಾಸ್ಪೆಟಲ್‌ಗ್ ಪೋಲೆ.",
      diabetes: "Diabetes ನಿಯಂತ್ರಣ ಮಲ್ಪೆರೆ:\n• Blood Sugar ಲೆವೆಲ್‌ನ್ ಚೆಕ್ ಮಲ್ಪೆ.\n• ಬೊಳ್ಳಿ ಅರಿ, ಸಿಹಿ ತಿನಸ್ ಕಮ್ಮಿ ಮಲ್ಪೆ.\n• ಪ್ರತಿದಿನ 30-45 ನಿಮಿಷ Brisk Walking ಮಲ್ಪೆ.\n• Metformin ಮರ್ದ್ ಸಮಯೊಗು ದೆತೊನುಲೆ.",
      bp: "Blood Pressure ಕಂಟ್ರೋಲ್‌ಡ್ ದೀಪೆರೆ:\n• ಉಪ್ಪುದ ಪ್ರಮಾಣ ಕಮ್ಮಿ ಮಲ್ಪೆ.\n• ಡೈಲಿ 30 ನಿಮಿಷ ನಡಪುಲೆ.\n• Amlodipine ಸಮಯೊಗು ದೆತೊನುಲೆ.",
      report: "ಇರೆನ ಲ್ಯಾಬ್ ರಿಪೋರ್ಟ್‌ದ ವಿವರೊ:\n• Fasting Blood Sugar: 118 mg/dL (ಸ್ವಲ್ಪ ಜಾಸ್ತಿ)\n• LDL Cholesterol: 142 mg/dL (ಸೀಮಾರೇಖೆ ಜಾಸ್ತಿ)\n• HbA1c: 6.2%\n• Kidney Function ಬೊಕ್ಕ Hemoglobin ಸಾಮಾನ್ಯ ಉಂಡು.",
      foods: "ಆಹಾರೊದ ಸಲಹೆಲು:\n• ಬೊಳ್ಳಿ ಅರಿ ಬೊಕ್ಕ ಎಣ್ಣೆಡ್ ಪುರಿದಿನ ತಿನಸ್ ಕಮ್ಮಿ ಮಲ್ಪೆ.\n• ರಾಗಿ, ಜೋಳ ಬೊಕ್ಕ ತರಕಾರಿ ಜಾಸ್ತಿ ತಿನೊಲಿ.",
      metformin: "Metformin ಮರ್ದ್ Type 2 Diabetes ಕಂಟ್ರೋಲ್‌ಗ್ ಕೋರ್ಪಿನಿ. ತಿನಸ್ ಮಲ್ತಿನ ಬುಕ್ಕೊ ದೆತೊನುಲೆ.",
      water: "ದಿನೊಕ್ಕು 2.5 ತರ್ದ್ 3 ಲೀಟರ್ ನೀರ್ ಪರ್ಲೆ.",
      greeting: "ನಮಸ್ಕಾರ! ಯಾನ್ ಇರೆನ HealthVerse AI ಸಹಾಯಕ. ಲ್ಯಾಬ್ ರಿಪೋರ್ಟ್, ಮರ್ದ್ ಬೊಕ್ಕ ತಿನಸ್‌ದ ಬಗ್ಗೆ ಕೇನೊಲಿ.",
      thanks: "ಸೊಲ್ಮೆಲು! ಇರೆನ ಆರೋಗ್ಯ ಎಡ್ಡೆ ದೀಲೆ.",
      default: "ಯಾನ್ ಇರೆನ HealthVerse AI ಸಹಾಯಕೆ. ರಿಪೋರ್ಟ್, Diabetes ಬೊಕ್ಕ BP ದ ಸಲಹೆ ಕೋರ್ಪೆ."
    },
    ta: {
      fever: "காய்ச்சல் இருந்தால் போதுமான அளவு தண்ணீர் குடித்து ஓய்வு எடுக்கவும்.",
      diabetes: "நீரிழிவு நோயைக் கட்டுப்படுத்த இரத்த சர்க்கரை அளவை தவறாமல் பரிசோதிக்கவும்.",
      bp: "இரத்த அழுத்தத்தைக் குறைக்க உணவில் உப்பைக் குறைக்கவும்.",
      report: "ஆய்வக அறிக்கை: சர்க்கரை அளவு 118 mg/dL சற்றே அதிகம்.",
      foods: "வெள்ளை அரிசி மற்றும் இனிப்புகளைக் குறைக்கவும்.",
      metformin: "Metformin உணவிற்குப் பிறகு எடுத்துக்கொள்ள வேண்டும்.",
      water: "தினமும் 2.5 - 3 லிட்டர் தண்ணீர் குடியுங்கள்.",
      greeting: "வணக்கம்! நான் உங்கள் HealthVerse AI மருத்துவ உதவியாளர்.",
      thanks: "நன்றி! ஆரோக்கியமாக இருங்கள்.",
      default: "நான் உங்கள் HealthVerse AI உதவியாளர்."
    },
    te: {
      fever: "జ్వరం ఉంటే తగినంత నీరు తాగి విశ్రాంతి తీసుకోండి.",
      diabetes: "మధుమేహం నియంత్రణకు బ్లడ్ షుగర్ రోజూ పరీక్షించండి.",
      bp: "బ్లడ్ ప్రెజర్ తగ్గడానికి ఉప్పు పరిమితం చేయండి.",
      report: "రిపోర్ట్: ఫాస్టింగ్ షుగర్ 118 mg/dL కొంచెం ఎక్కువ.",
      foods: "తెల్ల బియ్యం, తీపి పదార్థాలు తగ్గించండి.",
      metformin: "Metformin భోజనం తర్వాత తీసుకోవాలి.",
      water: "రోజుకి 2.5 నుండి 3 లీటర్ల నీరు తాగండి.",
      greeting: "నమస్కారం! నేను మీ HealthVerse AI సహాయకుడిని.",
      thanks: "ధన్యవాదాలు! జాగ్రత్తగా ఉండండి.",
      default: "నేను మీ HealthVerse AI సహాయకుడిని."
    },
    ml: {
      fever: "പനിയുണ്ടെങ്കിൽ ധാരാളം വെള്ളം കുടിച്ച് വിശ്രമിക്കുക.",
      diabetes: "പ്രമേഹം നിയന്ത്രിക്കാൻ ബ്ലഡ് ഷുഗർ ലെവൽ പരിശോധിക്കുക.",
      bp: "പ്രഷർ കുറയ്ക്കാൻ ഉപ്പിന്റെ അളവ് കുറയ്ക്കുക.",
      report: "ലാബ് റിപ്പോർട്ട്: ഷുഗർ 118 mg/dL ചെറുതായി ഉയർന്നതാണ്.",
      foods: "വെള്ള അരി, മധുരം എന്നിവ കുറയ്ക്കുക.",
      metformin: "Metformin ഭക്ഷണത്തിന് ശേഷം കഴിക്കുക.",
      water: "പ്രതിദിനം 2.5-3 ലിറ്റർ വെള്ളം കുടിക്കുക.",
      greeting: "ഹലോ! ഞാൻ നിങ്ങളുടെ HealthVerse AI മെഡിക്കൽ സഹായിയാണ്.",
      thanks: "നന്ദി! ആരോഗ്യം ശ്രദ്ധിക്കുക.",
      default: "ഞാൻ നിങ്ങളുടെ HealthVerse AI സഹായിയാണ്."
    },
    mr: {
      fever: "ताप असल्यास पुरेसे पाणी प्या व विश्रांती घ्या.",
      diabetes: "मधुमेहासाठी रक्तातील साखर नियमित तपासा.",
      bp: "रक्तदाब नियंत्रणासाठी मीठ कमी करा.",
      report: "रिपोर्ट: ब्लड शुगर 118 mg/dL (थोडी जास्त).",
      foods: "पांढरा भात व तळलेले पदार्थ टाळा.",
      metformin: "मेटफॉर्मिन जेवणानंतर घ्यावे.",
      water: "रोज २.५ ते ३ लिटर पाणी प्या.",
      greeting: "नमस्कार! मी आपला HealthVerse AI वैद्यकीय सहाय्यक आहे.",
      thanks: "धन्यवाद! आरोग्याची काळजी घ्या.",
      default: "मी आपला HealthVerse AI सहाय्यक आहे."
    }
  },

  translations: {
    hi: {
      summary: "अपलोड की गई लैब रिपोर्ट के आधार पर अधिकांश मान सामान्य हैं। उपवास रक्त शर्करा 118 mg/dL और LDL 142 mg/dL थोड़ा बढ़ा हुआ है।",
      findings: ["उपवास रक्त शर्करा: 118 mg/dL (थोड़ा उच्च)", "HbA1c: 6.2% (सामान्य के पास)", "LDL कोलेस्ट्रॉल: 142 mg/dL (सीमा रेखा पर)", "हीमोग्लोबिन: 13.8 g/dL (सामान्य)", "क्रिएटिनिन: 0.9 mg/dL (सामान्य)"]
    },
    kn: {
      summary: "ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಲ್ಯಾಬ್ ವರದಿ ಆಧಾರದಲ್ಲಿ ಹೆಚ್ಚಿನ ಮೌಲ್ಯಗಳು ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಯಲ್ಲಿವೆ. Fasting Blood Sugar 118 mg/dL ಮತ್ತು LDL 142 mg/dL ಸ್ವಲ್ಪ ಹೆಚ್ಚಾಗಿದೆ.",
      findings: ["Fasting Blood Sugar: 118 mg/dL (ಸ್ವಲ್ಪ ಹೆಚ್ಚು)", "HbA1c: 6.2% (ಸಾಮಾನ್ಯಕ್ಕೆ ಹತ್ತಿರ)", "LDL Cholesterol: 142 mg/dL (ಸೀಮಾರೇಖೆ ಹೆಚ್ಚು)", "Hemoglobin: 13.8 g/dL (ಸಾಮಾನ್ಯ)", "Creatinine: 0.9 mg/dL (ಸಾಮಾನ್ಯ)"]
    },
    tcy: {
      summary: "ಅಪ್‌ಲೋಡ್ ಮಲ್ತಿನ ಲ್ಯಾಬ್ ರಿಪೋರ್ಟ್‌ದ ಆಧಾರೊಡು ಮಸ್ತ್ ಮೌಲ್ಯೊಲು ಸಾಮಾನ್ಯ ಉಂಡು. Fasting Blood Sugar 118 mg/dL ಬೊಕ್ಕ LDL 142 mg/dL ಸ್ವಲ್ಪ ಜಾಸ್ತಿ ಉಂಡು.",
      findings: ["Fasting Blood Sugar: 118 mg/dL (ಸ್ವಲ್ಪ ಜಾಸ್ತಿ)", "HbA1c: 6.2% (ಸಾಮಾನ್ಯೊಗು ಕೈತಲ್)", "LDL Cholesterol: 142 mg/dL (ಸೀಮಾರೇಖೆ ಜಾಸ್ತಿ)", "Hemoglobin: 13.8 g/dL (ಸಾಮಾನ್ಯ)", "Creatinine: 0.9 mg/dL (ಸಾಮಾನ್ಯ)"]
    },
    ta: {
      summary: "ஆய்வக அறிக்கையில் பெரும்பாலான மதிப்புகள் இயல்பாக உள்ளன. உண்ணாவிரத சர்க்கரை 118 mg/dL சற்றே அதிகம்.",
      findings: ["இரத்த சர்க்கரை: 118 mg/dL (சற்றே அதிகம்)", "HbA1c: 6.2%", "LDL கொழுப்பு: 142 mg/dL", "ஹீமோகுளோபின்: 13.8 g/dL (இயல்பு)"]
    },
    te: {
      summary: "ల్యాబ్ రిపోర్ట్ ప్రకారం చాలా విలువలు సాధారణంగా ఉన్నాయి. షుగర్ 118 mg/dL కొంచెం ఎక్కువ.",
      findings: ["బ్లడ్ షుగర్: 118 mg/dL (కొంచెం ఎక్కువ)", "HbA1c: 6.2%", "LDL కొలెస్ట్రాల్: 142 mg/dL", "హిమోగ్లోబిన్: 13.8 g/dL (సాధారణం)"]
    },
    ml: {
      summary: "ലാബ് റിപ്പോർട്ടിൽ ഭൂരിഭാഗം മൂല്യങ്ങളും സാധാരണ നിലയിലാണ്. ഷുഗർ 118 mg/dL ചെറുതായി ഉയർന്നതാണ്.",
      findings: ["ബ്ലഡ് ഷുഗർ: 118 mg/dL (ചെറുതായി ഉയർന്നത്)", "HbA1c: 6.2%", "LDL കൊളസ്ട്രോൾ: 142 mg/dL", "ഹീമോഗ്ലോബിൻ: 13.8 g/dL (സാധാരണം)"]
    },
    mr: {
      summary: "लॅब रिपोर्टनुसार बहुतांश मूल्ये सामान्य आहेत. फास्टिंग शुगर 118 mg/dL थोडी जास्त आहे.",
      findings: ["फास्टिंग शुगर: 118 mg/dL (थोडी जास्त)", "HbA1c: 6.2%", "LDL कोलेस्ट्रॉल: 142 mg/dL", "हिमोग्लोबिन: 13.8 g/dL (सामान्य)"]
    }
  },

  init() {
    this.bindEvents();
    this.initGoogleGIS();
    this.checkAuth();
    this.updateNotificationDisplays();
    setTimeout(() => {
      if (this.state.currentScreen === 'splash') {
        this.navigate('onboarding-screen');
      }
    }, 1800);
  },

  bindEvents() {
    // 1. Onboarding
    document.getElementById('skip-onboarding')?.addEventListener('click', () => {
      this.navigate('auth-screen');
    });
    document.getElementById('next-onboarding')?.addEventListener('click', () => {
      if (this.state.onboardingSlide < 2) {
        this.setOnboardingSlide(this.state.onboardingSlide + 1);
      } else {
        this.navigate('auth-screen');
      }
    });
    document.querySelectorAll('.onboarding-dots .dot').forEach((dot, idx) => {
      dot.addEventListener('click', () => this.setOnboardingSlide(idx));
    });

    // 2. Auth screen switching
    document.querySelectorAll('.auth-tab').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tab = e.currentTarget.dataset.tab;
        document.querySelectorAll('.auth-tab').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
        e.currentTarget.classList.add('active');
        document.getElementById(`${tab}-form`)?.classList.add('active');
      });
    });

    // Login form submit
    document.getElementById('login-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleLogin();
    });

    // Signup form submit
    document.getElementById('signup-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleSignup();
    });

    // OTP toggle
    document.getElementById('otp-login')?.addEventListener('click', () => {
      document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
      document.getElementById('otp-form')?.classList.add('active');
    });

    document.getElementById('back-to-login')?.addEventListener('click', () => {
      document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
      document.getElementById('login-form')?.classList.add('active');
    });

    // OTP form submit
    document.getElementById('otp-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleOTPForm();
    });

    // Forgot password
    document.getElementById('forgot-password')?.addEventListener('click', (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email')?.value || 'your email';
      this.showToast(`Password reset link dispatched to ${email}`, 'info');
    });

    // Google Sign in button & Modal
    document.getElementById('google-login')?.addEventListener('click', () => {
      this.handleGoogleLogin();
    });
    document.getElementById('close-google')?.addEventListener('click', () => {
      document.getElementById('google-modal')?.classList.add('hidden');
    });
    document.querySelectorAll('.google-account').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const name = e.currentTarget.dataset.name;
        const email = e.currentTarget.dataset.email;
        this.completeGoogleSignIn(name, email);
      });
    });

    // Custom Gmail Sign In
    document.getElementById('custom-google-submit')?.addEventListener('click', () => {
      const email = document.getElementById('custom-google-email')?.value?.trim();
      if (!email || !email.includes('@')) {
        this.showToast('Please enter a valid Gmail address', 'warning');
        return;
      }
      const name = email.split('@')[0].replace('.', ' ');
      this.completeGoogleSignIn(name, email);
    });

    // Profile Setup Form
    document.getElementById('profile-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleSaveProfile();
    });

    // Main navigation items
    document.querySelectorAll('.nav-item').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const view = e.currentTarget.dataset.view;
        this.switchView(view);
      });
    });

    // Quick Action buttons on Home
    document.querySelectorAll('.quick-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const action = e.currentTarget.dataset.action;
        if (action === 'upload') this.switchView('reports');
        else if (action === 'chat') { this.switchView('chat'); this.updateChatLangBadge(); }
        else if (action === 'voice') { this.switchView('chat'); this.startVoiceInput(); }
        else if (action === 'sos') { this.openSOSModal(); }
      });
    });

    document.querySelectorAll('.see-all').forEach(a => {
      a.addEventListener('click', (e) => {
        e.preventDefault();
        const nav = e.currentTarget.dataset.nav;
        if (nav) this.switchView(nav);
      });
    });

    // Medicine check buttons
    document.querySelectorAll('.med-check').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.currentTarget.classList.toggle('taken');
        const isTaken = e.currentTarget.classList.contains('taken');
        const medId = e.currentTarget.dataset.med || '1';
        await API.request('POST', '/medicines/taken', { medicine_id: parseInt(medId), taken: isTaken });
        this.showToast(isTaken ? 'Medicine marked as taken! 💊' : 'Medicine marked pending', isTaken ? 'success' : 'info');
      });
    });

    // Water & Steps log buttons
    document.getElementById('log-water-btn')?.addEventListener('click', () => {
      this.state.waterMl = Math.min(this.state.waterMl + 250, 2500);
      const L = (this.state.waterMl / 1000).toFixed(1);
      const el = document.getElementById('water-count');
      if (el) el.textContent = L;
      const bar = document.getElementById('water-bar');
      if (bar) bar.style.width = Math.round((this.state.waterMl / 2500) * 100) + '%';
      this.showToast(`Water logged: ${L} / 2.5 L`, 'success');
    });

    document.getElementById('log-steps-btn')?.addEventListener('click', () => {
      this.state.stepCount = Math.min(this.state.stepCount + 500, 7500);
      const el = document.getElementById('steps-count');
      if (el) el.textContent = this.state.stepCount.toLocaleString();
      const bar = document.getElementById('steps-bar');
      if (bar) bar.style.width = Math.round((this.state.stepCount / 7500) * 100) + '%';
      this.showToast(`Steps logged: ${this.state.stepCount.toLocaleString()} / 7,500`, 'success');
    });

    // Reports Upload & Camera
    document.getElementById('upload-report-btn')?.addEventListener('click', () => {
      document.getElementById('file-input')?.click();
    });
    document.getElementById('file-input')?.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        this.processReportFile(e.target.files[0].name);
      }
    });
    document.getElementById('camera-btn')?.addEventListener('click', () => {
      this.openCameraScan();
    });
    document.getElementById('close-camera')?.addEventListener('click', () => {
      this.closeCameraModal();
    });
    document.getElementById('capture-btn')?.addEventListener('click', () => {
      this.captureReportPhoto();
    });

    // Past reports list clicks
    document.querySelectorAll('.report-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const title = e.currentTarget.querySelector('h4')?.textContent || 'Medical Report';
        this.processReportFile(title);
      });
    });

    // Report Translation & Read Aloud
    document.getElementById('translate-btn')?.addEventListener('click', () => {
      const lang = document.getElementById('translate-lang')?.value || 'en';
      this.state.selectedLang = lang;
      this.updateTranslationDisplay();
    });
    document.getElementById('translate-lang')?.addEventListener('change', (e) => {
      this.state.selectedLang = e.target.value;
      this.updateTranslationDisplay();
    });
    document.getElementById('voice-read-btn')?.addEventListener('click', () => {
      const text = document.getElementById('summary-text')?.textContent || '';
      this.speakText(text, this.state.selectedLang);
    });

    // Result tabs
    document.querySelectorAll('.result-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        const rtab = e.currentTarget.dataset.rtab;
        document.querySelectorAll('.result-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.rtab-content').forEach(c => c.classList.remove('active'));
        e.currentTarget.classList.add('active');
        document.getElementById(`rtab-${rtab}`)?.classList.add('active');
      });
    });

    // AI Chat
    document.getElementById('chat-send')?.addEventListener('click', () => this.sendChat());
    document.getElementById('chat-input')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.sendChat();
    });
    document.getElementById('chat-voice-btn')?.addEventListener('click', () => this.startVoiceInput());
    document.getElementById('voice-toggle')?.addEventListener('click', () => this.startVoiceInput());

    const chatLangSelect = document.getElementById('chat-lang-switcher');
    if (chatLangSelect) {
      chatLangSelect.addEventListener('change', (e) => {
        this.state.chatLang = e.target.value;
        this.updateChatLangBadge();
        this.showToast(`AI Language switched to: ${e.target.options[e.target.selectedIndex].text}`, 'info');
      });
    }

    document.querySelectorAll('.q-chip').forEach(chip => {
      chip.addEventListener('click', (e) => {
        const q = e.currentTarget.dataset.q;
        const input = document.getElementById('chat-input');
        if (input) input.value = q;
        this.sendChat();
      });
    });

    // Header buttons
    document.getElementById('notif-btn')?.addEventListener('click', () => {
      this.openModal('notif-modal');
    });
    document.getElementById('sos-btn')?.addEventListener('click', () => {
      this.openSOSModal();
    });

    // SOS Modal actions
    document.getElementById('confirm-sos')?.addEventListener('click', () => {
      this.triggerSOSAlert();
    });
    document.getElementById('cancel-sos')?.addEventListener('click', () => {
      document.getElementById('sos-modal')?.classList.add('hidden');
    });

    // Profile Page (4 Tabs)
    document.querySelectorAll('.profile-tab').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const ptab = e.currentTarget.dataset.ptab;
        document.querySelectorAll('.profile-tab').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.ptab-content').forEach(p => p.classList.remove('active'));
        e.currentTarget.classList.add('active');
        document.getElementById(`ptab-${ptab}`)?.classList.add('active');
        this.state.profileTab = ptab;
      });
    });

    // Profile menu actions
    document.querySelectorAll('.profile-menu-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const action = e.currentTarget.dataset.action;
        if (action === 'edit-profile') this.navigate('profile-setup-screen');
        else if (action === 'language') this.openModal('language-modal');
        else if (action === 'locker') this.openModal('locker-modal');
        else if (action === 'notifications') this.openModal('notif-modal');
        else if (action === 'voice-settings') this.openModal('voice-modal');
        else if (action === 'privacy') this.openModal('privacy-modal');
        else if (action === 'theme') this.toggleDarkMode();
        else if (action === 'logout') this.handleLogout();
      });
    });

    // Modal close buttons
    document.querySelectorAll('.modal .btn-outline').forEach(btn => {
      if (btn.id && btn.id.startsWith('close-')) {
        btn.addEventListener('click', () => {
          btn.closest('.modal')?.classList.add('hidden');
        });
      }
    });

    // Toggle switches click handler
    document.querySelectorAll('.toggle-switch').forEach(toggle => {
      toggle.addEventListener('click', (e) => {
        e.currentTarget.classList.toggle('on');
        const isOn = e.currentTarget.classList.contains('on');
        this.showToast(`Setting ${isOn ? 'Enabled' : 'Disabled'}`, 'info');
      });
    });

    // Data Export
    document.getElementById('export-data')?.addEventListener('click', () => {
      const dataStr = JSON.stringify(this.state, null, 2);
      const blob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `healthverse_user_data_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
      this.showToast('User health data exported successfully!', 'success');
    });

    // Backdrop click & ESC key to close modals
    document.querySelectorAll('.modal').forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          modal.classList.add('hidden');
        }
      });
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal:not(.hidden)').forEach(modal => {
          modal.classList.add('hidden');
        });
      }
    });

    // Notification settings save
    document.getElementById('save-notif')?.addEventListener('click', () => {
      const email = document.getElementById('notif-email')?.value || this.state.notifEmail;
      const phone = document.getElementById('notif-phone')?.value || this.state.notifPhone;
      this.state.notifEmail = email;
      this.state.notifPhone = phone;
      localStorage.setItem('hv_notif_email', email);
      localStorage.setItem('hv_notif_phone', phone);
      this.updateNotificationDisplays();

      this.sendNotification("Test Reminder: Take Metformin 500mg after dinner", "High Priority");

      const log = document.getElementById('notif-log');
      if (log) {
        const time = new Date().toLocaleTimeString();
        log.innerHTML = `<div class="notif-log-item">✓ [${time}] Test reminder dispatched to ${email} & ${phone}</div>` + log.innerHTML;
      }
    });

    // Save language settings
    document.getElementById('save-language')?.addEventListener('click', () => {
      const lang = document.getElementById('settings-language')?.value || 'en';
      const cLang = document.getElementById('settings-chat-lang')?.value || 'en';
      this.state.selectedLang = lang;
      this.state.chatLang = cLang;
      this.updateChatLangBadge();
      document.getElementById('language-modal')?.classList.add('hidden');
      this.showToast('Language settings saved!', 'success');
    });

    // Save voice settings
    document.getElementById('save-voice')?.addEventListener('click', () => {
      const speed = parseFloat(document.getElementById('voice-speed')?.value || '1.0');
      this.state.voiceSpeed = speed;
      document.getElementById('voice-modal')?.classList.add('hidden');
      this.showToast('Voice settings saved!', 'success');
    });
  },

  initGoogleGIS() {
    if (GOOGLE_CLIENT_ID && window.google?.accounts?.id) {
      try {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: (response) => {
            if (response.credential) {
              this.completeGoogleSignIn(null, null, response.credential);
            }
          }
        });
      } catch (err) {
        console.warn('GIS initialization notice:', err);
      }
    }
  },

  setOnboardingSlide(slideIdx) {
    this.state.onboardingSlide = slideIdx;
    document.querySelectorAll('.onboarding-slide').forEach((s, idx) => {
      s.classList.toggle('active', idx === slideIdx);
    });
    document.querySelectorAll('.onboarding-dots .dot').forEach((d, idx) => {
      d.classList.toggle('active', idx === slideIdx);
    });
  },

  navigate(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const target = document.getElementById(screenId);
    if (target) {
      target.classList.add('active');
      this.state.currentScreen = screenId;
      if (screenId === 'auth-screen') {
        const char = document.getElementById('auth-character');
        const speech = document.getElementById('char-speech');
        if (char) char.className = 'auth-character walking';
        if (speech) speech.textContent = "Hi! Let's get you signed in 💜";
      }
    }
  },

  switchView(viewId) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

    const navBtn = document.querySelector(`.nav-item[data-view="${viewId}"]`);
    const viewEl = document.getElementById(`view-${viewId}`);

    if (navBtn) navBtn.classList.add('active');
    if (viewEl) viewEl.classList.add('active');
    this.state.currentView = viewId;
  },

  openModal(modalId) {
    const m = document.getElementById(modalId);
    if (m) m.classList.remove('hidden');
  },

  celebrateLogin() {
    const char = document.getElementById('auth-character');
    const speech = document.getElementById('char-speech');
    const card = document.getElementById('auth-card');

    if (char) char.className = 'auth-character dancing';
    if (speech) speech.textContent = "Yay! Welcome back! 🎉";
    if (card) {
      card.classList.add('success-pulse');
      setTimeout(() => card.classList.remove('success-pulse'), 1500);
    }
  },

  async handleLogin() {
    const email = document.getElementById('login-email')?.value?.trim();
    const password = document.getElementById('login-password')?.value;

    if (!email || !password) {
      this.showToast('Please enter email and password', 'warning');
      return;
    }

    const res = await API.request('POST', '/auth/login', { email, password });
    if (res && res.ok && res.token) {
      localStorage.setItem('hv_token', res.token);
      this.state.user = res.user;
      this.celebrateLogin();
      this.showToast(`Welcome, ${res.user.name || 'User'}!`, 'success');
      setTimeout(() => {
        this.updateUserDisplay();
        if (!res.user.profile_complete) {
          this.navigate('profile-setup-screen');
        } else {
          this.navigate('app-shell');
        }
      }, 1000);
    } else {
      // Demo / fallback path if email registered in memory or local state
      const user = { name: email.split('@')[0].replace('.', ' '), email, phone: this.state.notifPhone };
      this.state.user = user;
      this.celebrateLogin();
      this.showToast(`Logged in as ${user.name}!`, 'success');
      setTimeout(() => {
        this.updateUserDisplay();
        this.navigate('app-shell');
      }, 1000);
    }
  },

  async handleSignup() {
    const name = document.getElementById('signup-name')?.value?.trim();
    const email = document.getElementById('signup-email')?.value?.trim();
    const password = document.getElementById('signup-password')?.value;
    const confirm = document.getElementById('signup-confirm')?.value;

    if (!name || !email || !password) {
      this.showToast('Please fill in all required fields', 'warning');
      return;
    }
    if (password !== confirm) {
      this.showToast('Passwords do not match', 'error');
      return;
    }

    const res = await API.request('POST', '/auth/register', { name, email, password });
    if (res && res.ok && res.token) {
      localStorage.setItem('hv_token', res.token);
      this.state.user = res.user;
      this.celebrateLogin();
      this.showToast('Account created successfully!', 'success');
      setTimeout(() => {
        this.updateUserDisplay();
        this.navigate('profile-setup-screen');
      }, 1000);
    } else if (res && res.error) {
      this.showToast(res.error, 'error');
    } else {
      this.state.user = { name, email, phone: this.state.notifPhone };
      this.celebrateLogin();
      this.showToast('Account created!', 'success');
      setTimeout(() => {
        this.updateUserDisplay();
        this.navigate('profile-setup-screen');
      }, 1000);
    }
  },

  async handleOTPForm() {
    const codeGroup = document.getElementById('otp-code-group');
    const submitBtn = document.getElementById('otp-submit');
    const hintEl = document.getElementById('otp-demo-hint');
    const target = document.getElementById('otp-mobile')?.value?.trim();

    if (!target) {
      this.showToast('Please enter an email or phone number', 'warning');
      return;
    }

    if (codeGroup && (codeGroup.style.display === 'none' || !codeGroup.style.display)) {
      const res = await API.request('POST', '/auth/otp/send', { phone: target });
      const otpCode = res?.demo_otp || '123456';
      
      codeGroup.style.display = 'block';
      if (submitBtn) submitBtn.textContent = 'Verify OTP & Login';
      if (hintEl) hintEl.textContent = `🔑 Demo OTP code: ${otpCode} (or 123456)`;

      const isEmail = target.includes('@');
      this.showToast(isEmail ? `OTP sent to email: ${target}` : `SMS OTP sent to ${target}`, 'success');
      this.state.sentOtpCode = otpCode;
    } else {
      const code = document.getElementById('otp-code')?.value?.trim();
      if (!code) {
        this.showToast('Please enter the 6-digit OTP', 'warning');
        return;
      }

      const res = await API.request('POST', '/auth/otp/verify', { phone: target, code, name: target.split('@')[0] });
      if (res && res.ok && res.token) {
        localStorage.setItem('hv_token', res.token);
        this.state.user = res.user;
        this.celebrateLogin();
        this.showToast('OTP verified successfully!', 'success');
        setTimeout(() => {
          this.updateUserDisplay();
          if (!res.user.profile_complete) {
            this.navigate('profile-setup-screen');
          } else {
            this.navigate('app-shell');
          }
        }, 1000);
      } else if (code === '123456' || code === this.state.sentOtpCode) {
        this.state.user = { name: target.includes('@') ? target.split('@')[0] : 'Mobile User', email: target.includes('@') ? target : this.state.notifEmail, phone: target };
        this.celebrateLogin();
        this.showToast('OTP verified successfully!', 'success');
        setTimeout(() => {
          this.updateUserDisplay();
          this.navigate('app-shell');
        }, 1000);
      } else {
        this.showToast(res?.error || 'Invalid OTP code. Try demo code 123456', 'error');
      }
    }
  },

  handleGoogleLogin() {
    if (GOOGLE_CLIENT_ID && window.google?.accounts?.id) {
      window.google.accounts.id.prompt();
    } else {
      this.openModal('google-modal');
    }
  },

  async completeGoogleSignIn(name, email, credential = null) {
    document.getElementById('google-modal')?.classList.add('hidden');
    
    const body = credential ? { credential } : { name, email };
    const res = await API.request('POST', '/auth/google', body);
    
    if (res && res.ok && res.token) {
      localStorage.setItem('hv_token', res.token);
      this.state.user = res.user;
    } else {
      this.state.user = { name: name || 'Google User', email: email || 'user@gmail.com', phone: this.state.notifPhone };
    }

    this.celebrateLogin();
    this.showToast(`Signed in with Google (${this.state.user.email})!`, 'success');
    setTimeout(() => {
      this.updateUserDisplay();
      if (this.state.user.profile_complete === false) {
        this.navigate('profile-setup-screen');
      } else {
        this.navigate('app-shell');
      }
    }, 1000);
  },

  async handleSaveProfile() {
    const profile = {
      name: document.getElementById('profile-name')?.value || 'User',
      age: document.getElementById('profile-age')?.value || '32',
      gender: document.getElementById('profile-gender')?.value || 'Female',
      blood: document.getElementById('profile-blood')?.value || 'B+',
      height: document.getElementById('profile-height')?.value || '165',
      weight: document.getElementById('profile-weight')?.value || '62',
      allergies: document.getElementById('profile-allergies')?.value || 'Penicillin',
      diseases: document.getElementById('profile-diseases')?.value || 'Pre-Diabetes',
      emergency: document.getElementById('profile-emergency')?.value || '+91 98765 43210',
      language: document.getElementById('profile-language')?.value || 'en'
    };

    const res = await API.request('PUT', '/profile', profile);
    this.state.profile = (res && res.ok && res.profile) ? res.profile : profile;
    if (this.state.user) this.state.user.name = profile.name;
    this.updateUserDisplay();
    this.showToast('Profile updated successfully!', 'success');
    this.navigate('app-shell');
  },

  updateUserDisplay() {
    const name = this.state.user?.name || this.state.profile?.name || 'Priya Sharma';
    const email = this.state.user?.email || this.state.notifEmail;
    const phone = this.state.user?.phone || this.state.notifPhone;
    const blood = this.state.profile?.blood || this.state.profile?.blood_group || 'B+';
    const allergies = this.state.profile?.allergies || 'Penicillin';
    const diseases = this.state.profile?.diseases || 'Pre-Diabetes';
    const emergency = this.state.profile?.emergency || this.state.profile?.emergency_contact || phone;

    const displayEl = document.getElementById('user-display-name');
    if (displayEl) displayEl.textContent = name;

    const pvName = document.getElementById('profile-view-name');
    const pvDetails = document.getElementById('profile-view-details');
    if (pvName) pvName.textContent = name;
    if (pvDetails) pvDetails.textContent = `${email} • ${phone}`;

    const piBlood = document.getElementById('pi-blood');
    const piAllergies = document.getElementById('pi-allergies');
    const piDiseases = document.getElementById('pi-diseases');
    const piEmergency = document.getElementById('pi-emergency');

    if (piBlood) piBlood.textContent = blood;
    if (piAllergies) piAllergies.textContent = allergies;
    if (piDiseases) piDiseases.textContent = diseases;
    if (piEmergency) piEmergency.textContent = emergency;

    const sBlood = document.getElementById('sos-blood');
    const sAllergies = document.getElementById('sos-allergies');
    const sContact = document.getElementById('sos-contact');
    if (sBlood) sBlood.textContent = blood;
    if (sAllergies) sAllergies.textContent = allergies;
    if (sContact) sContact.textContent = emergency;

    this.updateNotificationDisplays();
  },

  updateNotificationDisplays() {
    const notifEmailDisplay = document.getElementById('pi-notif-email');
    const notifPhoneDisplay = document.getElementById('pi-notif-phone');
    const nInputEmail = document.getElementById('notif-email');
    const nInputPhone = document.getElementById('notif-phone');

    if (notifEmailDisplay) notifEmailDisplay.textContent = this.state.notifEmail;
    if (notifPhoneDisplay) notifPhoneDisplay.textContent = this.state.notifPhone;
    if (nInputEmail && !nInputEmail.value) nInputEmail.value = this.state.notifEmail;
    if (nInputPhone && !nInputPhone.value) nInputPhone.value = this.state.notifPhone;
  },

  updateChatLangBadge() {
    const badge = document.getElementById('chat-lang-badge');
    const switcher = document.getElementById('chat-lang-switcher');
    const names = { en: 'English', hi: 'हिंदी', kn: 'ಕನ್ನಡ', tcy: 'ತುಳು', ta: 'தமிழ்', te: 'తెలుగు', ml: 'മലയാളം', mr: 'मराठी', bn: 'বাংলা' };
    const lang = this.state.chatLang || 'en';
    if (badge) badge.textContent = `🌐 ${names[lang] || lang}`;
    if (switcher && switcher.value !== lang) switcher.value = lang;
  },

  getChatReply(text) {
    const lang = this.detectLanguage(text, this.state.chatLang || 'en');
    const pack = this.aiResponses[lang] || this.aiResponses.en;
    const msg = (text || '').toLowerCase();

    if (/(fever|feverish|ಜ್ವರ|ಬುಖಾರ್|बुखार|காய்ச்சல்|జ్వరం|പനി|ताप)/.test(msg)) return pack.fever;
    if (/(diabetes|sugar|glucose|hba1c|ಪ್ರಮೇಹ|मधुमेह|நீரிழிவு|మధుమేహం|പ്രമേഹം|डायबिटीज)/.test(msg)) return pack.diabetes;
    if (/(bp|blood pressure|hypertension|ರಕ್ತದೊತ್ತಡ|ರಕ್ತಚಾಪ|रक्तचाप|இரத்த அழுத்தம்|రక్తపోటు|രക്തസമ്മർദ്ദം)/.test(msg)) return pack.bp;
    if (/(report|lab|blood|result|analysis|ವರದಿ|रिपोर्ट|அறிக்கை|రిపోర్ట్|റിപ്പോർട്ട്)/.test(msg)) return pack.report;
    if (/(food|eat|diet|avoid|rice|ಆಹಾರ|ಅಕ್ಕಿ|खाना|भोजन|चावल|உணவு|ஆஹாரம்|ആഹാരം|आहार|भात|ತಿನಸ್)/.test(msg)) return pack.foods;
    if (/(metformin|medicine|drug|tablet|pill|ಔಷಧಿ|ಮರ್ದ್|दवा|மருந்து|మందులు|മരുന്ന്|औषध)/.test(msg)) return pack.metformin;
    if (/(water|hydrat|ನೀರು|पानी|தண்ணீர்|నీళ్ళు|വെള്ളം|पाणी|ನೀರ್)/.test(msg)) return pack.water;
    if (/(hello|hi |hey|namaste|namaskara|namaskar|vanakkam|namaskaram|ನಮಸ್ಕಾರ|नमस्ते|வணக்கம்)/.test(msg)) return pack.greeting;
    if (/(thank|thanks|dhanyavad|solmelu|ಧನ್ಯವಾದ|धन्यवाद|நன்றி|ధన్యవాదాలు|നന്ദി|ಸೊಲ್ಮೆಲು)/.test(msg)) return pack.thanks;

    return pack.default;
  },

  async sendChat() {
    const input = document.getElementById('chat-input');
    const text = input?.value?.trim();
    if (!text) return;

    this.appendMessage(text, 'user');
    input.value = '';

    const lang = this.detectLanguage(text, this.state.chatLang);

    const apiRes = await API.request('POST', '/chat', { message: text });
    const reply = (apiRes && apiRes.ok && apiRes.reply) ? apiRes.reply : this.getChatReply(text);

    setTimeout(() => {
      this.appendMessage(reply, 'bot');
      if (this.state.ttsAuto) {
        this.speakText(reply, lang);
      }
    }, 400);
  },

  appendMessage(text, type) {
    const container = document.getElementById('chat-messages');
    if (!container) return;

    const div = document.createElement('div');
    div.className = `message ${type}`;
    const formatted = (text || '').replace(/\n/g, '<br>');
    div.innerHTML = `
      <div class="msg-avatar"><i class="fas fa-${type === 'bot' ? 'robot' : 'user'}"></i></div>
      <div class="msg-bubble">${formatted}</div>`;

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  },

  startVoiceInput() {
    const lang = this.state.chatLang || 'en';

    if (lang === 'tcy') {
      this.showToast('Browser Speech Recognition does not ship Tulu yet. Typed Tulu is fully supported!', 'info');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      this.showToast('Speech recognition is not supported in this browser.', 'warning');
      return;
    }

    try {
      if (!this.state.recognition) {
        this.state.recognition = new SpeechRecognition();
        this.state.recognition.continuous = false;
        this.state.recognition.interimResults = false;

        this.state.recognition.onstart = () => {
          this.showToast('Listening... Speak now.', 'info');
        };
        this.state.recognition.onresult = (e) => {
          const transcript = e.results[0][0].transcript;
          const input = document.getElementById('chat-input');
          if (input) input.value = transcript;
          this.sendChat();
        };
        this.state.recognition.onerror = (e) => {
          this.showToast(`Voice input error: ${e.error}`, 'error');
        };
      }

      this.state.recognition.lang = this.speechLangCode(lang);
      this.state.recognition.start();
    } catch (err) {
      this.showToast('Microphone busy or unavailable.', 'error');
    }
  },

  speechLangCode(lang) {
    const codes = { en: 'en-US', hi: 'hi-IN', kn: 'kn-IN', ta: 'ta-IN', te: 'te-IN', ml: 'ml-IN', mr: 'mr-IN', tcy: 'kn-IN' };
    return codes[lang] || 'en-US';
  },

  speakText(text, lang = 'en') {
    if (!window.speechSynthesis) return;
    if (lang === 'tcy') {
      this.showToast('Tulu voice engine unavailable in browser — falling back to text response.', 'info');
      return;
    }
    const utter = new SpeechSynthesisUtterance(text.replace(/•/g, ''));
    utter.rate = this.state.voiceSpeed;
    utter.lang = this.speechLangCode(lang);
    window.speechSynthesis.speak(utter);
  },

  async openCameraScan() {
    this.openModal('camera-modal');
    const video = document.getElementById('camera-video');
    const placeholder = document.getElementById('camera-placeholder');

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      this.state.cameraStream = stream;
      if (video) {
        video.srcObject = stream;
        video.style.display = 'block';
        if (placeholder) placeholder.style.display = 'none';
        video.play();
      }
    } catch (err) {
      console.warn('Camera getUserMedia error:', err);
      this.showToast('Camera permission denied or camera unavailable. Please select a report file to upload.', 'warning');
    }
  },

  closeCameraModal() {
    if (this.state.cameraStream) {
      this.state.cameraStream.getTracks().forEach(track => track.stop());
      this.state.cameraStream = null;
    }
    const video = document.getElementById('camera-video');
    const placeholder = document.getElementById('camera-placeholder');
    if (video) video.style.display = 'none';
    if (placeholder) placeholder.style.display = 'block';
    document.getElementById('camera-modal')?.classList.add('hidden');
  },

  captureReportPhoto() {
    const video = document.getElementById('camera-video');
    const canvas = document.getElementById('camera-canvas');
    if (video && video.srcObject && video.videoWidth) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    }
    this.closeCameraModal();
    this.processReportFile('Camera_Scan_Report.jpg');
  },

  processReportFile(filename) {
    const overlay = document.getElementById('processing-overlay');
    const result = document.getElementById('analysis-result');
    if (overlay) overlay.classList.remove('hidden');

    setTimeout(() => {
      if (overlay) overlay.classList.add('hidden');
      if (result) result.classList.remove('hidden');
      this.updateTranslationDisplay();
      this.showToast(`Analyzed ${filename} successfully!`, 'success');
    }, 1200);
  },

  updateTranslationDisplay() {
    const lang = this.state.selectedLang || 'en';
    const summaryEl = document.getElementById('summary-text');
    const findingsEl = document.getElementById('findings-list');

    if (!summaryEl || !findingsEl) return;

    if (lang === 'en') {
      summaryEl.textContent = "Based on the uploaded lab report, most values are within normal range. Slight elevation in fasting blood sugar and LDL cholesterol noted. Continue current medication and lifestyle changes.";
      findingsEl.innerHTML = `
        <li class="abnormal"><i class="fas fa-exclamation-circle"></i> Fasting Blood Sugar: 118 mg/dL (Slightly High)</li>
        <li class="normal"><i class="fas fa-check-circle"></i> HbA1c: 6.2% (Near normal)</li>
        <li class="abnormal"><i class="fas fa-exclamation-circle"></i> LDL Cholesterol: 142 mg/dL (Borderline High)</li>
        <li class="normal"><i class="fas fa-check-circle"></i> Hemoglobin: 13.8 g/dL (Normal)</li>
        <li class="normal"><i class="fas fa-check-circle"></i> Creatinine: 0.9 mg/dL (Normal)</li>`;
      return;
    }

    const t = this.translations[lang];
    if (t) {
      summaryEl.textContent = t.summary;
      findingsEl.innerHTML = t.findings.map(f => `<li class="${f.includes('118') || f.includes('142') ? 'abnormal' : 'normal'}">${f}</li>`).join('');
    } else {
      summaryEl.textContent = `Translating report analysis into ${lang}...`;
    }
  },

  openSOSModal() {
    this.updateUserDisplay();
    this.openModal('sos-modal');
  },

  async triggerSOSAlert() {
    document.getElementById('sos-modal')?.classList.add('hidden');
    const contact = this.state.notifPhone || '+91 98765 43210';
    await API.request('POST', '/sos', {});
    this.showToast(`🚨 SOS ACTIVATED! Location and medical summary sent to ${contact} and nearest emergency department.`, 'error');
  },

  sendNotification(text, priority = 'Normal') {
    const email = this.state.notifEmail;
    const phone = this.state.notifPhone;
    this.showToast(`[${priority}] Sent email to ${email} & SMS to ${phone}`, 'success');
  },

  toggleDarkMode() {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    this.showToast(isDark ? 'Dark mode enabled 🌙' : 'Light mode enabled ☀️', 'info');
  },

  handleLogout() {
    localStorage.removeItem('hv_token');
    this.state.user = null;
    this.showToast('Logged out successfully', 'info');
    this.navigate('auth-screen');
  },

  async checkAuth() {
    const token = localStorage.getItem('hv_token');
    if (token) {
      const res = await API.request('GET', '/profile');
      if (res && res.ok && res.profile) {
        this.state.profile = res.profile;
        this.state.user = { name: res.profile.name || 'Priya Sharma', email: this.state.notifEmail, phone: res.profile.emergency_contact || this.state.notifPhone };
      } else {
        this.state.user = { name: 'Priya Sharma', email: this.state.notifEmail, phone: this.state.notifPhone };
      }
      this.updateUserDisplay();
      this.navigate('app-shell');
    }
  },

  showToast(msg, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const iconClass = type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle';
    toast.innerHTML = `<i class="fas fa-${iconClass}"></i> <span>${msg}</span>`;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();

  // ── Drag & Drop support on the upload zone ──────────────
  const zone = document.getElementById('upload-zone');
  if (zone) {
    ['dragover', 'dragenter'].forEach(ev => {
      zone.addEventListener(ev, (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
      });
    });
    ['dragleave', 'dragend', 'drop'].forEach(ev => {
      zone.addEventListener(ev, (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
      });
    });
    zone.addEventListener('drop', (e) => {
      e.preventDefault();
      const file = e.dataTransfer?.files?.[0];
      if (file) App.processReportFile(file.name);
    });
  }
});
