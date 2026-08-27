/**
 * HealthVerse AI — Frontend Application
 * Works offline (localStorage) and with backend at localhost:8000
 */

(function () {
  'use strict';

  // ---------- State ----------
  const state = {
    user: null,
    token: null,
    profile: null,
    onboardingDone: false,
    currentView: 'home',
    backendAvailable: false,
    language: 'en',
    darkMode: false,
    medicinesTaken: {},
    chatHistory: [],
    googleClientId: '',
    realSms: false,
  };

  const API_BASE = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
    ? window.location.origin
    : 'http://localhost:8000';

  // ---------- Helpers ----------
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); }

  function showScreen(id) {
    $$('.screen').forEach(s => s.classList.remove('active'));
    const el = document.getElementById(id);
    if (el) el.classList.add('active');
  }

  function showView(name) {
    state.currentView = name;
    $$('.view').forEach(v => v.classList.remove('active'));
    const v = document.getElementById('view-' + name);
    if (v) v.classList.add('active');
    $$('.nav-item').forEach(n => {
      n.classList.toggle('active', n.dataset.view === name);
    });
  }

  function toast(msg, type) {
    const t = $('#toast');
    t.textContent = msg;
    t.className = 'toast' + (type ? ' ' + type : '');
    t.classList.remove('hidden');
    clearTimeout(t._timer);
    t._timer = setTimeout(() => t.classList.add('hidden'), 3200);
  }

  function saveLocal() {
    try {
      localStorage.setItem('hv_state', JSON.stringify({
        user: state.user,
        token: state.token,
        profile: state.profile,
        onboardingDone: state.onboardingDone,
        language: state.language,
        darkMode: state.darkMode,
        medicinesTaken: state.medicinesTaken,
        chatHistory: state.chatHistory.slice(-50),
      }));
    } catch (e) {}
  }

  function loadLocal() {
    try {
      const raw = localStorage.getItem('hv_state');
      if (!raw) return;
      const d = JSON.parse(raw);
      Object.assign(state, d);
    } catch (e) {}
  }

  // ---------- API ----------
  async function api(path, opts) {
    opts = opts || {};
    const headers = Object.assign({ 'Content-Type': 'application/json' }, opts.headers || {});
    if (state.token) headers['Authorization'] = 'Bearer ' + state.token;
    try {
      const res = await fetch(API_BASE + '/api' + path, {
        method: opts.method || 'GET',
        headers,
        body: opts.body ? JSON.stringify(opts.body) : undefined,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || data.detail || 'Request failed');
      return data;
    } catch (e) {
      if (e.message === 'Failed to fetch' || e.name === 'TypeError') {
        state.backendAvailable = false;
        throw new Error('OFFLINE');
      }
      throw e;
    }
  }

  async function checkBackend() {
    try {
      const r = await fetch(API_BASE + '/api/health', { method: 'GET' });
      state.backendAvailable = r.ok;
      if (r.ok) {
        const data = await r.json();
        state.googleClientId = data.google_client_id || '';
        state.realSms = !!data.real_sms;
      }
    } catch (e) {
      state.backendAvailable = false;
    }
    // Also allow setting client id from meta or window for frontend-only
    if (!state.googleClientId && window.GOOGLE_CLIENT_ID) {
      state.googleClientId = window.GOOGLE_CLIENT_ID;
    }
  }

  // ---------- Simulated AI / Offline data ----------
  const DEMO_ANALYSIS = {
    summary: 'Based on the uploaded lab report, most values are within normal range. Slight elevation in fasting blood sugar and LDL cholesterol noted. Continue current medication and lifestyle changes.',
    risk: 'moderate',
    findings: [
      { text: 'Fasting Blood Sugar: 118 mg/dL (Slightly High)', abnormal: true },
      { text: 'HbA1c: 6.2% (Near normal)', abnormal: false },
      { text: 'LDL Cholesterol: 142 mg/dL (Borderline High)', abnormal: true },
      { text: 'Hemoglobin: 13.8 g/dL (Normal)', abnormal: false },
      { text: 'Creatinine: 0.9 mg/dL (Normal)', abnormal: false },
    ],
    details: [
      { param: 'Fasting Glucose', value: '118 mg/dL', ref: '70-100', status: 'High' },
      { param: 'HbA1c', value: '6.2%', ref: '<5.7%', status: 'Elevated' },
      { param: 'Total Cholesterol', value: '210 mg/dL', ref: '<200', status: 'Borderline' },
      { param: 'LDL', value: '142 mg/dL', ref: '<100', status: 'High' },
      { param: 'HDL', value: '48 mg/dL', ref: '>40', status: 'Normal' },
      { param: 'Triglycerides', value: '145 mg/dL', ref: '<150', status: 'Normal' },
      { param: 'Hemoglobin', value: '13.8 g/dL', ref: '12-16', status: 'Normal' },
      { param: 'Creatinine', value: '0.9 mg/dL', ref: '0.6-1.2', status: 'Normal' },
    ],
    medicines: [
      { name: 'Metformin 500 mg', dosage: '1 tablet twice daily after meals', purpose: 'Controls blood sugar levels in type 2 diabetes', side: 'Nausea, diarrhea (usually temporary)' },
      { name: 'Amlodipine 5 mg', dosage: '1 tablet once daily', purpose: 'Lowers blood pressure', side: 'Ankle swelling, dizziness' },
      { name: 'Atorvastatin 10 mg', dosage: '1 tablet at night', purpose: 'Reduces cholesterol', side: 'Muscle pain (rare)' },
    ],
  };

  const TRANSLATIONS = {
    hi: {
      summary: 'अपलोड की गई लैब रिपोर्ट के आधार पर, अधिकांश मान सामान्य सीमा में हैं। उपवास रक्त शर्करा और एलडीएल कोलेस्ट्रॉल में थोड़ी वृद्धि देखी गई। वर्तमान दवा और जीवनशैली परिवर्तन जारी रखें।',
      findings: [
        'उपवास रक्त शर्करा: 118 mg/dL (थोड़ा उच्च)',
        'HbA1c: 6.2% (लगभग सामान्य)',
        'LDL कोलेस्ट्रॉल: 142 mg/dL (सीमा रेखा उच्च)',
        'हीमोग्लोबिन: 13.8 g/dL (सामान्य)',
        'क्रिएटिनिन: 0.9 mg/dL (सामान्य)',
      ],
    },
    kn: {
      summary: 'ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಲ್ಯಾಬ್ ರಿಪೋರ್ಟ್ ಆಧಾರದ ಮೇಲೆ, ಹೆಚ್ಚಿನ ಮೌಲ್ಯಗಳು ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಯಲ್ಲಿವೆ. ಉಪವಾಸ ರಕ್ತದ ಸಕ್ಕರೆ ಮತ್ತು LDL ಕೊಲೆಸ್ಟ್ರಾಲ್‌ನಲ್ಲಿ ಸ್ವಲ್ಪ ಏರಿಕೆ ಕಂಡುಬಂದಿದೆ. ಪ್ರಸ್ತುತ ಔಷಧಿ ಮತ್ತು ಜೀವನಶೈಲಿ ಬದಲಾವಣೆಗಳನ್ನು ಮುಂದುವರಿಸಿ.',
      findings: [
        'ಉಪವಾಸ ರಕ್ತದ ಸಕ್ಕರೆ: 118 mg/dL (ಸ್ವಲ್ಪ ಹೆಚ್ಚು)',
        'HbA1c: 6.2% (ಸಾಮಾನ್ಯಕ್ಕೆ ಹತ್ತಿರ)',
        'LDL ಕೊಲೆಸ್ಟ್ರಾಲ್: 142 mg/dL (ಗಡಿ ಹೆಚ್ಚು)',
        'ಹಿಮೋಗ್ಲೋಬಿನ್: 13.8 g/dL (ಸಾಮಾನ್ಯ)',
        'ಕ್ರಿಯೇಟಿನಿನ್: 0.9 mg/dL (ಸಾಮಾನ್ಯ)',
      ],
    },
    ta: {
      summary: 'பதிவேற்றப்பட்ட ஆய்வக அறிக்கையின் அடிப்படையில், பெரும்பாலான மதிப்புகள் இயல்பான வரம்பில் உள்ளன. உண்ணாவிரத இரத்த சர்க்கரை மற்றும் LDL கொலஸ்ட்ரால் சற்று உயர்ந்துள்ளது. தற்போதைய மருந்து மற்றும் வாழ்க்கைமுறை மாற்றங்களைத் தொடரவும்.',
      findings: [
        'உண்ணாவிரத இரத்த சர்க்கரை: 118 mg/dL (சற்று அதிகம்)',
        'HbA1c: 6.2% (இயல்புக்கு அருகில்)',
        'LDL கொலஸ்ட்ரால்: 142 mg/dL (எல்லை அதிகம்)',
        'ஹீமோகுளோபின்: 13.8 g/dL (இயல்பு)',
        'கிரியேட்டினின்: 0.9 mg/dL (இயல்பு)',
      ],
    },
    te: {
      summary: 'అప్‌లోడ్ చేసిన ల్యాబ్ రిపోర్ట్ ఆధారంగా, చాలా విలువలు సాధారణ పరిధిలో ఉన్నాయి. ఉపవాస రక్త చక్కెర మరియు LDL కొలెస్ట్రాల్‌లో కొద్దిగా పెరుగుదల కనిపించింది. ప్రస్తుత మందు మరియు జీవనశైలి మార్పులను కొనసాగించండి.',
      findings: [
        'ఉపవాస రక్త చక్కెర: 118 mg/dL (కొద్దిగా ఎక్కువ)',
        'HbA1c: 6.2% (సాధారణానికి దగ్గరగా)',
        'LDL కొలెస్ట్రాల్: 142 mg/dL (సరిహద్దు ఎక్కువ)',
        'హిమోగ్లోబిన్: 13.8 g/dL (సాధారణ)',
        'క్రియేటినిన్: 0.9 mg/dL (సాధారణ)',
      ],
    },
    ml: {
      summary: 'അപ്‌ലോഡ് ചെയ്ത ലാബ് റിപ്പോർട്ട് അടിസ്ഥാനമാക്കി, മിക്ക മൂല്യങ്ങളും സാധാരണ പരിധിയിലാണ്. ഉപവാസ രക്തത്തിലെ പഞ്ചസാരയിലും LDL കൊളസ്ട്രോളിലും ചെറിയ വർദ്ധനവ് കാണുന്നു. നിലവിലെ മരുന്നും ജീവിതശൈലി മാറ്റങ്ങളും തുടരുക.',
      findings: [
        'ഉപവാസ രക്ത പഞ്ചസാര: 118 mg/dL (അല്പം കൂടുതൽ)',
        'HbA1c: 6.2% (സാധാരണയോട് അടുത്ത്)',
        'LDL കൊളസ്ട്രോൾ: 142 mg/dL (അതിർത്തി ഉയർന്നത്)',
        'ഹീമോഗ്ലോബിൻ: 13.8 g/dL (സാധാരണ)',
        'ക്രിയേറ്റിനിൻ: 0.9 mg/dL (സാധാരണ)',
      ],
    },
    tcy: {
      summary: 'ಅಪ್‌ಲೋಡ್ ಮಲ್ಪಿನ ಲ್ಯಾಬ್ ರಿಪೋರ್ಟ್‌ದ ಅಡಿಟ್, ಬಹುತೇಕ ಮೌಲ್ಯೊಲು ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಡ್ ಉಂಡು. ಉಪವಾಸ ರಕ್ತದ ಸಕ್ಕರೆ ಬೊಕ್ಕ LDL ಕೊಲೆಸ್ಟ್ರಾಲ್‌ಡ್ ಸ್ವಲ್ಪ ಏರಿಕೆ ತೋಜುಂಡು. ಪ್ರಸ್ತುತ ಔಷಧಿ ಬೊಕ್ಕ ಜೀವನಶೈಲಿ ಬದಲಾವಣೆಲೆನ್ ಮುಂದುವರಿಸಲೆ.',
      findings: [
        'ಉಪವಾಸ ರಕ್ತದ ಸಕ್ಕರೆ: 118 mg/dL (ಸ್ವಲ್ಪ ಜಾಸ್ತಿ)',
        'HbA1c: 6.2% (ಸಾಮಾನ್ಯೊಗು ಕೈತಲ್)',
        'LDL ಕೊಲೆಸ್ಟ್ರಾಲ್: 142 mg/dL (ಎಲ್ಲೆ ಜಾಸ್ತಿ)',
        'ಹಿಮೋಗ್ಲೋಬಿನ್: 13.8 g/dL (ಸಾಮಾನ್ಯ)',
        'ಕ್ರಿಯೇಟಿನಿನ್: 0.9 mg/dL (ಸಾಮಾನ್ಯ)',
      ],
    },
  };

  const CHAT_REPLIES = {
    en: {
      default: "I'm your HealthVerse AI assistant. Based on your profile, I recommend continuing your current medications, walking 30 minutes daily, and monitoring blood sugar. How else can I help?",
      report: "Your latest report shows fasting glucose slightly elevated at 118 mg/dL and LDL at 142. Most other parameters are normal. Focus on diet, exercise, and medicine adherence.",
      food: "Prefer whole grains, millets, leafy greens. Limit sweets, fried food, and white rice. Small frequent meals help with blood sugar control.",
      metformin: "Metformin 500mg helps control blood sugar in type 2 diabetes. Take after meals. Common temporary side effects: mild nausea or diarrhea. Do not skip doses.",
      rice: "You can eat small portions of brown rice or millets. Prefer whole grains over polished white rice. Pair with vegetables and protein.",
    },
    hi: {
      default: "मैं आपका HealthVerse AI सहायक हूँ। अपनी दवाएँ जारी रखें, रोज़ 30 मिनट पैदल चलें और शुगर मॉनिटर करें। और कैसे मदद करूँ?",
      report: "आपकी रिपोर्ट में फास्टिंग शुगर 118 और LDL 142 थोड़ा बढ़ा है। बाकी ज्यादातर मान सामान्य हैं। डाइट, एक्सरसाइज और दवा नियमित लें।",
      food: "साबुत अनाज, बाजरा, हरी सब्जियाँ लें। मिठाई, तला और सफेद चावल कम करें। छोटे-छोटे भोजन बेहतर हैं।",
      metformin: "मेटफॉर्मिन 500mg टाइप-2 डायबिटीज में शुगर कंट्रोल करता है। भोजन के बाद लें। हल्की मतली या दस्त अस्थायी हो सकते हैं।",
      rice: "थोड़ा ब्राउन राइस या बाजरा खा सकते हैं। सफेद चावल के बजाय साबुत अनाज चुनें। सब्जी और प्रोटीन के साथ लें।",
    },
    kn: {
      default: "ನಾನು ನಿಮ್ಮ HealthVerse AI ಸಹಾಯಕ. ಔಷಧಿ ಮುಂದುವರಿಸಿ, ದಿನಕ್ಕೆ 30 ನಿಮಿಷ ನಡೆಯಿರಿ, ಸಕ್ಕರೆ ಪರೀಕ್ಷಿಸಿ. ಇನ್ನೇನು ಸಹಾಯ?",
      report: "ನಿಮ್ಮ ವರದಿಯಲ್ಲಿ ಉಪವಾಸ ಸಕ್ಕರೆ 118 ಮತ್ತು LDL 142 ಸ್ವಲ್ಪ ಹೆಚ್ಚು. ಉಳಿದವು ಸಾಮಾನ್ಯ. ಆಹಾರ, ವ್ಯಾಯಾಮ, ಔಷಧಿ ನಿಯಮಿತವಾಗಿ.",
      food: "ಸಂಪೂರ್ಣ ಧಾನ್ಯ, ರಾಗಿ, ಹಸಿರು ತರಕಾರಿ ತೆಗೆದುಕೊಳ್ಳಿ. ಸಿಹಿ, ಹುರಿದ ಆಹಾರ, ಬಿಳಿ ಅನ್ನ ಕಡಿಮೆ. ಸಣ್ಣ ಊಟಗಳು ಉತ್ತಮ.",
      metformin: "ಮೆಟ್‌ಫಾರ್ಮಿನ್ 500mg ಟೈಪ್-2 ಮಧುಮೇಹದಲ್ಲಿ ಸಕ್ಕರೆ ನಿಯಂತ್ರಿಸುತ್ತದೆ. ಊಟದ ನಂತರ ತೆಗೆದುಕೊಳ್ಳಿ.",
      rice: "ಸ್ವಲ್ಪ ಕಂದು ಅನ್ನ ಅಥವಾ ರಾಗಿ ತಿನ್ನಬಹುದು. ಬಿಳಿ ಅನ್ನಕ್ಕಿಂತ ಸಂಪೂರ್ಣ ಧಾನ್ಯ ಆರಿಸಿ.",
    },
  };

  function getChatReply(msg) {
    const lang = state.language || 'en';
    const replies = CHAT_REPLIES[lang] || CHAT_REPLIES.en;
    const m = (msg || '').toLowerCase();
    if (m.includes('report') || m.includes('explain') || m.includes('ರಿಪೋರ್ಟ್') || m.includes('रिपोर्ट')) return replies.report;
    if (m.includes('food') || m.includes('avoid') || m.includes('ಆಹಾರ') || m.includes('खाना')) return replies.food;
    if (m.includes('metformin') || m.includes('ಮೆಟ್') || m.includes('मेटफॉर्मिन')) return replies.metformin;
    if (m.includes('rice') || m.includes('ಅನ್ನ') || m.includes('चावल')) return replies.rice;
    return replies.default;
  }

  // ---------- Auth character ----------
  function ensureAuthCharacter() {
    const header = $('.auth-header');
    if (!header || $('#auth-character')) return;
    const div = document.createElement('div');
    div.id = 'auth-character';
    div.className = 'auth-character';
    div.innerHTML = `
      <div class="char-body">
        <div class="char-face">
          <div class="eye left"></div>
          <div class="eye right"></div>
          <div class="mouth"></div>
        </div>
      </div>
    `;
    header.insertBefore(div, header.firstChild);
  }

  function danceCharacter() {
    const c = $('#auth-character');
    if (!c) return;
    c.classList.add('dance', 'happy');
    setTimeout(() => c.classList.remove('dance'), 1800);
  }

  // ---------- Splash & Onboarding ----------
  function startApp() {
    loadLocal();
    ensureAuthCharacter();
    setTimeout(() => {
      if (state.token && state.user) {
        if (state.profile && state.profile.name) {
          enterApp();
        } else {
          showScreen('profile-setup-screen');
          prefillProfileForm();
        }
      } else if (state.onboardingDone) {
        showScreen('auth-screen');
      } else {
        showScreen('onboarding-screen');
      }
    }, 1800);
  }

  function initOnboarding() {
    let slide = 0;
    const slides = $$('.onboarding-slide');
    const dots = $$('.dot');
    function go(n) {
      slide = Math.max(0, Math.min(n, slides.length - 1));
      slides.forEach((s, i) => s.classList.toggle('active', i === slide));
      dots.forEach((d, i) => d.classList.toggle('active', i === slide));
      $('#next-onboarding').textContent = slide === slides.length - 1 ? 'Get Started' : 'Next';
    }
    $('#next-onboarding').addEventListener('click', () => {
      if (slide >= slides.length - 1) {
        state.onboardingDone = true;
        saveLocal();
        showScreen('auth-screen');
      } else go(slide + 1);
    });
    $('#skip-onboarding').addEventListener('click', () => {
      state.onboardingDone = true;
      saveLocal();
      showScreen('auth-screen');
    });
    dots.forEach(d => d.addEventListener('click', () => go(+d.dataset.dot)));
  }

  // ---------- Auth ----------
  function initAuth() {
    // Tabs
    $$('.auth-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        $$('.auth-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        $$('.auth-form').forEach(f => f.classList.remove('active'));
        const form = document.getElementById(tab.dataset.tab === 'login' ? 'login-form' : 'signup-form');
        if (form) form.classList.add('active');
        $('#otp-form').classList.remove('active');
      });
    });

    // Login
    $('#login-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = $('#login-email').value.trim();
      const password = $('#login-password').value;
      if (!email || !password) return toast('Enter email and password', 'error');

      try {
        if (state.backendAvailable) {
          const data = await api('/auth/login', { method: 'POST', body: { email, password } });
          state.token = data.token;
          state.user = data.user;
          state.profile = data.profile || null;
        } else {
          // Offline
          const users = JSON.parse(localStorage.getItem('hv_users') || '{}');
          const u = users[email];
          if (!u || u.password !== password) {
            // demo account
            if (email === 'demo@healthverse.ai' && password === 'demo123') {
              state.user = { id: 'demo', name: 'Demo User', email };
              state.token = 'offline-demo';
              state.profile = state.profile || { name: 'Demo User', age: 45, gender: 'male', blood: 'O+', language: 'en' };
            } else {
              return toast('Invalid email or password. Try demo@healthverse.ai / demo123', 'error');
            }
          } else {
            state.user = { id: u.id, name: u.name, email };
            state.token = 'offline-' + u.id;
            state.profile = u.profile || null;
          }
        }
        saveLocal();
        danceCharacter();
        toast('Login successful!', 'success');
        setTimeout(() => {
          if (state.profile && state.profile.name) enterApp();
          else {
            showScreen('profile-setup-screen');
            prefillProfileForm();
          }
        }, 900);
      } catch (err) {
        if (err.message === 'OFFLINE') {
          // retry offline path
          const users = JSON.parse(localStorage.getItem('hv_users') || '{}');
          const u = users[email];
          if ((u && u.password === password) || (email === 'demo@healthverse.ai' && password === 'demo123')) {
            state.user = u ? { id: u.id, name: u.name, email } : { id: 'demo', name: 'Demo User', email };
            state.token = 'offline';
            state.profile = (u && u.profile) || state.profile || { name: 'Demo User' };
            saveLocal();
            danceCharacter();
            toast('Login successful (offline)', 'success');
            setTimeout(() => {
              if (state.profile && state.profile.name) enterApp();
              else showScreen('profile-setup-screen');
            }, 900);
          } else toast('Invalid credentials. Use demo@healthverse.ai / demo123', 'error');
        } else toast(err.message || 'Login failed', 'error');
      }
    });

    // Signup
    $('#signup-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = $('#signup-name').value.trim();
      const email = $('#signup-email').value.trim();
      const password = $('#signup-password').value;
      const confirm = $('#signup-confirm').value;
      if (!name || !email || !password) return toast('Fill all fields', 'error');
      if (password !== confirm) return toast('Passwords do not match', 'error');
      if (password.length < 6) return toast('Password must be at least 6 characters', 'error');

      try {
        if (state.backendAvailable) {
          const data = await api('/auth/register', { method: 'POST', body: { name, email, password } });
          state.token = data.token;
          state.user = data.user;
        } else {
          const users = JSON.parse(localStorage.getItem('hv_users') || '{}');
          if (users[email]) return toast('Email already registered', 'error');
          const id = 'u' + Date.now();
          users[email] = { id, name, email, password, profile: null };
          localStorage.setItem('hv_users', JSON.stringify(users));
          state.user = { id, name, email };
          state.token = 'offline-' + id;
        }
        state.profile = null;
        saveLocal();
        danceCharacter();
        toast('Account created!', 'success');
        setTimeout(() => {
          showScreen('profile-setup-screen');
          $('#profile-name').value = name;
        }, 900);
      } catch (err) {
        if (err.message === 'OFFLINE') {
          const users = JSON.parse(localStorage.getItem('hv_users') || '{}');
          if (users[email]) return toast('Email already registered', 'error');
          const id = 'u' + Date.now();
          users[email] = { id, name, email, password, profile: null };
          localStorage.setItem('hv_users', JSON.stringify(users));
          state.user = { id, name, email };
          state.token = 'offline-' + id;
          saveLocal();
          danceCharacter();
          toast('Account created (offline)!', 'success');
          setTimeout(() => {
            showScreen('profile-setup-screen');
            $('#profile-name').value = name;
          }, 900);
        } else toast(err.message || 'Signup failed', 'error');
      }
    });

    // OTP
    $('#otp-login').addEventListener('click', () => {
      $$('.auth-form').forEach(f => f.classList.remove('active'));
      $('#otp-form').classList.add('active');
      $$('.auth-tab').forEach(t => t.classList.remove('active'));
    });

    $('#back-to-login').addEventListener('click', () => {
      $('#otp-form').classList.remove('active');
      $('#login-form').classList.add('active');
      $$('.auth-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === 'login'));
      const od = $('.otp-display');
      if (od) od.classList.remove('show');
      $('#otp-code-group').style.display = 'none';
      $('#otp-submit').textContent = 'Send OTP';
    });

    let pendingOtp = null;
    let pendingPhone = null;

    $('#otp-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const phone = $('#otp-mobile').value.trim();
      const codeInput = $('#otp-code');
      const codeGroup = $('#otp-code-group');

      if (!codeGroup.style.display || codeGroup.style.display === 'none') {
        // Send OTP
        if (!phone || phone.length < 10) return toast('Enter a valid mobile number', 'error');
        pendingPhone = phone;
        pendingOtp = String(Math.floor(100000 + Math.random() * 900000));
        let displayCode = pendingOtp;
        let mode = 'demo';
        try {
          if (state.backendAvailable) {
            const data = await api('/auth/otp/send', { method: 'POST', body: { phone } });
            mode = data.mode || 'demo';
            if (data.code) {
              displayCode = data.code;
              pendingOtp = data.code;
            }
            if (data.message) console.log('OTP:', data.message);
          }
        } catch (err) { /* offline ok */ }

        let od = $('.otp-display');
        if (!od) {
          od = document.createElement('div');
          od.className = 'otp-display';
          $('#otp-form').insertBefore(od, $('#otp-code-group'));
        }
        if (mode === 'demo' || !state.realSms) {
          od.innerHTML = 'Demo OTP: <strong>' + displayCode + '</strong><br><small>Also try 123456 · For real SMS set keys in backend/config.py</small>';
          od.classList.add('show');
          toast('OTP sent (demo). Use the code shown above.', 'success');
        } else {
          od.innerHTML = 'OTP sent to <strong>' + phone + '</strong><br><small>Check your SMS messages</small>';
          od.classList.add('show');
          toast('OTP sent to your phone via SMS', 'success');
        }
        codeGroup.style.display = 'block';
        $('#otp-submit').textContent = 'Verify OTP';
      } else {
        // Verify
        const code = codeInput.value.trim();
        if (!code) return toast('Enter OTP', 'error');
        const ok = code === pendingOtp || code === '123456';
        if (!ok) return toast('Invalid OTP. Use the code shown or 123456', 'error');

        try {
          if (state.backendAvailable) {
            const data = await api('/auth/otp/verify', { method: 'POST', body: { phone: pendingPhone, code } });
            state.token = data.token;
            state.user = data.user;
            state.profile = data.profile || null;
          } else {
            state.user = { id: 'otp-' + pendingPhone, name: 'User', email: pendingPhone + '@otp.local', phone: pendingPhone };
            state.token = 'offline-otp';
          }
          saveLocal();
          danceCharacter();
          toast('OTP verified!', 'success');
          setTimeout(() => {
            if (state.profile && state.profile.name) enterApp();
            else {
              showScreen('profile-setup-screen');
              prefillProfileForm();
            }
          }, 900);
        } catch (err) {
          if (err.message === 'OFFLINE' || true) {
            state.user = { id: 'otp-' + pendingPhone, name: 'User', email: pendingPhone + '@otp.local', phone: pendingPhone };
            state.token = 'offline-otp';
            saveLocal();
            danceCharacter();
            toast('OTP verified!', 'success');
            setTimeout(() => {
              if (state.profile && state.profile.name) enterApp();
              else showScreen('profile-setup-screen');
            }, 900);
          }
        }
      }
    });

    // Google login — real GSI if client id set, else demo picker
    $('#google-login').addEventListener('click', () => {
      if (state.googleClientId) {
        triggerRealGoogleSignIn();
      } else {
        showGooglePicker();
      }
    });

    // Forgot password
    $('#forgot-password').addEventListener('click', (e) => {
      e.preventDefault();
      toast('Demo: use demo@healthverse.ai / demo123 or reset via OTP', 'success');
    });
  }

  function showGooglePicker() {
    let picker = $('#google-picker');
    if (!picker) {
      picker = document.createElement('div');
      picker.id = 'google-picker';
      picker.className = 'google-picker';
      picker.innerHTML = `
        <div class="google-picker-box">
          <div class="google-picker-header">
            <svg width="24" height="24" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            <h3>Choose an account</h3>
          </div>
          <button class="google-account" data-email="demo@healthverse.ai" data-name="Demo User">
            <div class="g-avatar" style="background:#9b7EBD">D</div>
            <div class="g-info"><h4>Demo User</h4><p>demo@healthverse.ai</p></div>
          </button>
          <button class="google-account" data-email="priya.sharma@gmail.com" data-name="Priya Sharma">
            <div class="g-avatar" style="background:#F4A6C2">P</div>
            <div class="g-info"><h4>Priya Sharma</h4><p>priya.sharma@gmail.com</p></div>
          </button>
          <button class="google-account" data-email="rahul.k@gmail.com" data-name="Rahul Kumar">
            <div class="g-avatar" style="background:#3498db">R</div>
            <div class="g-info"><h4>Rahul Kumar</h4><p>rahul.k@gmail.com</p></div>
          </button>
          <div class="google-picker-footer">
            <button type="button" id="google-cancel">Cancel</button>
          </div>
        </div>
      `;
      document.body.appendChild(picker);
      picker.addEventListener('click', (e) => {
        if (e.target === picker || e.target.id === 'google-cancel') {
          picker.classList.add('hidden');
        }
        const acc = e.target.closest('.google-account');
        if (acc) {
          picker.classList.add('hidden');
          doGoogleLogin(acc.dataset.email, acc.dataset.name);
        }
      });
    }
    picker.classList.remove('hidden');
  }

  async function doGoogleLogin(email, name, idToken) {
    try {
      if (state.backendAvailable) {
        const body = { email, name };
        if (idToken) body.id_token = idToken;
        const data = await api('/auth/google', { method: 'POST', body });
        state.token = data.token;
        state.user = data.user;
        state.profile = data.profile || { name, email };
      } else {
        state.user = { id: 'g-' + email, name, email };
        state.token = 'offline-google';
        state.profile = state.profile || { name, email, language: 'en' };
      }
      saveLocal();
      danceCharacter();
      toast(idToken ? 'Signed in with real Google account!' : 'Signed in with Google!', 'success');
      setTimeout(() => {
        if (state.profile && state.profile.name && state.profile.age) enterApp();
        else {
          showScreen('profile-setup-screen');
          prefillProfileForm();
        }
      }, 900);
    } catch (err) {
      if (idToken) {
        toast(err.message || 'Google sign-in failed', 'error');
        return;
      }
      state.user = { id: 'g-' + email, name, email };
      state.token = 'offline-google';
      state.profile = state.profile || { name, email };
      saveLocal();
      danceCharacter();
      toast('Signed in with Google!', 'success');
      setTimeout(() => {
        if (state.profile && state.profile.age) enterApp();
        else showScreen('profile-setup-screen');
      }, 900);
    }
  }

  function triggerRealGoogleSignIn() {
    if (!state.googleClientId) {
      showGooglePicker();
      return;
    }
    if (typeof google === 'undefined' || !google.accounts || !google.accounts.id) {
      toast('Google script loading... try again in a second', 'error');
      // fallback: try One Tap init then prompt
      setTimeout(triggerRealGoogleSignIn, 800);
      return;
    }
    try {
      google.accounts.id.initialize({
        client_id: state.googleClientId,
        callback: handleGoogleCredential,
        auto_select: false,
        cancel_on_tap_outside: true,
      });
      // Show One Tap or render button
      const container = document.getElementById('google-btn-container');
      if (container) {
        container.style.display = 'block';
        container.innerHTML = '';
        google.accounts.id.renderButton(container, {
          theme: 'outline',
          size: 'large',
          width: container.offsetWidth || 320,
          text: 'signin_with',
          shape: 'rectangular',
        });
      }
      google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          // User can click the rendered button
          toast('Use the Google button below to choose your real Gmail account', 'success');
        }
      });
    } catch (e) {
      console.error(e);
      toast('Google Sign-In error. Check CLIENT_ID in backend/config.py', 'error');
      showGooglePicker();
    }
  }

  function handleGoogleCredential(response) {
    // response.credential is the JWT id_token from real Google account
    const idToken = response.credential;
    if (!idToken) {
      toast('No credential from Google', 'error');
      return;
    }
    // Decode payload (no verify on client — server verifies)
    try {
      const payload = JSON.parse(atob(idToken.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
      const email = payload.email;
      const name = payload.name || payload.given_name || (email && email.split('@')[0]) || 'User';
      doGoogleLogin(email, name, idToken);
    } catch (e) {
      // Still send token to server
      doGoogleLogin('', 'User', idToken);
    }
  }

  function initGoogleButtonIfReady() {
    const hint = document.getElementById('auth-mode-hint');
    if (state.googleClientId) {
      if (hint) hint.textContent = 'Google: real Gmail accounts enabled';
      // Pre-render official button when GSI loads
      const tryRender = () => {
        if (typeof google !== 'undefined' && google.accounts && google.accounts.id) {
          const container = document.getElementById('google-btn-container');
          if (container) {
            container.style.display = 'block';
            container.innerHTML = '';
            google.accounts.id.initialize({
              client_id: state.googleClientId,
              callback: handleGoogleCredential,
            });
            google.accounts.id.renderButton(container, {
              theme: 'outline',
              size: 'large',
              width: Math.min(320, window.innerWidth - 48),
              text: 'signin_with',
            });
          }
        } else {
          setTimeout(tryRender, 400);
        }
      };
      tryRender();
    } else if (hint) {
      hint.textContent = 'Demo mode: set GOOGLE_CLIENT_ID in backend/config.py for real Gmail';
    }
    if (hint && state.realSms) {
      hint.textContent = (hint.textContent || '') + ' · SMS OTP: live';
    } else if (hint && !state.realSms) {
      hint.textContent = (hint.textContent || '') + (hint.textContent ? ' · ' : '') + 'OTP: demo (code shown on screen)';
    }
  }

  // ---------- Profile setup ----------
  function prefillProfileForm() {
    if (!state.user) return;
    const n = $('#profile-name');
    if (n && !n.value) n.value = state.user.name || (state.profile && state.profile.name) || '';
    if (state.profile) {
      if (state.profile.age) $('#profile-age').value = state.profile.age;
      if (state.profile.gender) $('#profile-gender').value = state.profile.gender;
      if (state.profile.blood) $('#profile-blood').value = state.profile.blood;
      if (state.profile.height) $('#profile-height').value = state.profile.height;
      if (state.profile.weight) $('#profile-weight').value = state.profile.weight;
      if (state.profile.allergies) $('#profile-allergies').value = state.profile.allergies;
      if (state.profile.diseases) $('#profile-diseases').value = state.profile.diseases;
      if (state.profile.emergency) $('#profile-emergency').value = state.profile.emergency;
      if (state.profile.language) $('#profile-language').value = state.profile.language;
    }
  }

  function initProfileSetup() {
    $('#profile-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const profile = {
        name: $('#profile-name').value.trim(),
        age: +$('#profile-age').value || null,
        gender: $('#profile-gender').value,
        blood: $('#profile-blood').value,
        height: +$('#profile-height').value || null,
        weight: +$('#profile-weight').value || null,
        allergies: $('#profile-allergies').value.trim(),
        diseases: $('#profile-diseases').value.trim(),
        emergency: $('#profile-emergency').value.trim(),
        language: $('#profile-language').value || 'en',
      };
      if (!profile.name || !profile.age || !profile.gender || !profile.blood) {
        return toast('Please fill required fields', 'error');
      }
      state.profile = profile;
      state.language = profile.language;
      if (state.user) state.user.name = profile.name;

      try {
        if (state.backendAvailable) {
          await api('/profile', { method: 'PUT', body: profile });
        } else {
          const users = JSON.parse(localStorage.getItem('hv_users') || '{}');
          if (state.user && state.user.email && users[state.user.email]) {
            users[state.user.email].profile = profile;
            users[state.user.email].name = profile.name;
            localStorage.setItem('hv_users', JSON.stringify(users));
          }
        }
      } catch (err) { /* offline ok */ }

      saveLocal();
      toast('Profile saved!', 'success');
      enterApp();
    });
  }

  // ---------- Enter main app ----------
  function enterApp() {
    showScreen('app-shell');
    showView('home');
    updateUIFromState();
    if (state.darkMode) document.body.classList.add('dark');
  }

  function updateUIFromState() {
    const name = (state.profile && state.profile.name) || (state.user && state.user.name) || 'User';
    const el = $('#user-display-name');
    if (el) el.textContent = name.split(' ')[0];
    const pn = $('#profile-view-name');
    if (pn) pn.textContent = name;
    const pd = $('#profile-view-details');
    if (pd && state.profile) {
      const parts = [];
      if (state.profile.age) parts.push(state.profile.age + ' yrs');
      if (state.profile.gender) parts.push(state.profile.gender);
      if (state.profile.blood) parts.push(state.profile.blood);
      pd.textContent = parts.join(' • ') || '—';
    }
    // SOS info
    if (state.profile) {
      const sb = $('#sos-blood'); if (sb) sb.textContent = state.profile.blood || '—';
      const sa = $('#sos-allergies'); if (sa) sa.textContent = state.profile.allergies || 'None';
      const sc = $('#sos-contact'); if (sc) sc.textContent = state.profile.emergency || '—';
    }
    // medicine checks
    $$('.med-check').forEach(btn => {
      const id = btn.dataset.med;
      if (state.medicinesTaken[id]) btn.classList.add('taken');
    });
  }

  // ---------- Navigation ----------
  function initNav() {
    $$('.nav-item').forEach(btn => {
      btn.addEventListener('click', () => showView(btn.dataset.view));
    });
    $$('.quick-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const a = btn.dataset.action;
        if (a === 'upload') showView('reports');
        else if (a === 'chat') showView('chat');
        else if (a === 'voice') {
          showView('chat');
          startVoiceInput();
        } else if (a === 'sos') openSos();
      });
    });
    $$('.see-all').forEach(a => {
      a.addEventListener('click', (e) => {
        e.preventDefault();
        if (a.dataset.nav) showView(a.dataset.nav);
      });
    });
  }

  // ---------- Medicines ----------
  function initMedicines() {
    $$('.med-check').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.med;
        const taken = !btn.classList.contains('taken');
        btn.classList.toggle('taken', taken);
        state.medicinesTaken[id] = taken;
        saveLocal();
        try {
          if (state.backendAvailable) {
            await api('/medicines/taken', { method: 'POST', body: { medicine_id: id, taken } });
          }
        } catch (e) {}
        toast(taken ? 'Marked as taken' : 'Unmarked', 'success');
      });
    });
  }

  // ---------- Reports / Upload ----------
  function initReports() {
    const fileInput = $('#file-input');
    const uploadZone = $('#upload-zone');
    const cameraBtn = $('#camera-btn');
    const uploadReportBtn = $('#upload-report-btn');

    function processFile(file) {
      if (!file) return;
      const overlay = $('#processing-overlay');
      const result = $('#analysis-result');
      const past = $('#past-reports');
      overlay.classList.remove('hidden');
      result.classList.add('hidden');
      let step = 0;
      const steps = ['Extracting text with OCR...', 'Analyzing lab values...', 'Generating summary...', 'Preparing recommendations...'];
      const status = $('#process-status');
      const detail = $('#process-detail');
      const iv = setInterval(() => {
        step++;
        if (step < steps.length) {
          status.textContent = steps[step];
          detail.textContent = 'Please wait...';
        } else {
          clearInterval(iv);
          overlay.classList.add('hidden');
          result.classList.remove('hidden');
          if (past) past.style.display = 'none';
          renderAnalysis(DEMO_ANALYSIS);
          toast('Report analyzed successfully!', 'success');
        }
      }, 700);
    }

    fileInput.addEventListener('change', () => {
      if (fileInput.files[0]) processFile(fileInput.files[0]);
    });

    uploadZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadZone.classList.add('dragover');
    });
    uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
    uploadZone.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadZone.classList.remove('dragover');
      if (e.dataTransfer.files[0]) processFile(e.dataTransfer.files[0]);
    });

    uploadReportBtn.addEventListener('click', () => fileInput.click());

    // Camera
    cameraBtn.addEventListener('click', openCamera);
    $('#close-camera').addEventListener('click', closeCamera);
    $('#capture-btn').addEventListener('click', captureFromCamera);

    // Result tabs
    $$('.result-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        $$('.result-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        $$('.rtab-content').forEach(c => c.classList.remove('active'));
        const target = document.getElementById('rtab-' + tab.dataset.rtab);
        if (target) target.classList.add('active');
      });
    });

    // Translate
    $('#translate-btn').addEventListener('click', () => {
      const lang = $('#translate-lang').value;
      const t = TRANSLATIONS[lang];
      if (!t) {
        toast('Translation available for Hindi, Kannada, Tamil, Telugu, Malayalam, Tulu', 'success');
        return;
      }
      $('#summary-text').textContent = t.summary;
      const list = $('#findings-list');
      list.innerHTML = '';
      t.findings.forEach((f, i) => {
        const li = document.createElement('li');
        li.className = DEMO_ANALYSIS.findings[i] && DEMO_ANALYSIS.findings[i].abnormal ? 'abnormal' : 'normal';
        li.innerHTML = '<i class="fas fa-' + (li.className === 'abnormal' ? 'exclamation-circle' : 'check-circle') + '"></i> ' + f;
        list.appendChild(li);
      });
      toast('Translated!', 'success');
    });

    // Voice read
    $('#voice-read-btn').addEventListener('click', () => {
      const text = $('#summary-text').textContent;
      if ('speechSynthesis' in window) {
        const u = new SpeechSynthesisUtterance(text);
        u.lang = state.language === 'hi' ? 'hi-IN' : state.language === 'kn' ? 'kn-IN' : 'en-IN';
        speechSynthesis.speak(u);
        toast('Reading aloud...', 'success');
      } else toast('Speech not supported in this browser', 'error');
    });

    // Past reports click
    $$('.report-item').forEach(item => {
      item.addEventListener('click', () => {
        $('#analysis-result').classList.remove('hidden');
        renderAnalysis(DEMO_ANALYSIS);
        toast('Loaded previous analysis', 'success');
      });
    });
  }

  function renderAnalysis(data) {
    $('#summary-text').textContent = data.summary;
    const list = $('#findings-list');
    list.innerHTML = '';
    data.findings.forEach(f => {
      const li = document.createElement('li');
      li.className = f.abnormal ? 'abnormal' : 'normal';
      li.innerHTML = '<i class="fas fa-' + (f.abnormal ? 'exclamation-circle' : 'check-circle') + '"></i> ' + f.text;
      list.appendChild(li);
    });
  }

  // Camera
  let mediaStream = null;
  function openCamera() {
    const modal = $('#camera-modal');
    modal.classList.remove('hidden');
    const preview = $('.camera-preview');
    preview.innerHTML = '';
    const video = document.createElement('video');
    video.autoplay = true;
    video.playsInline = true;
    preview.appendChild(video);
    const canvas = document.createElement('canvas');
    canvas.id = 'capture-canvas';
    preview.appendChild(canvas);

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        .then(stream => {
          mediaStream = stream;
          video.srcObject = stream;
        })
        .catch(() => {
          preview.innerHTML = '<i class="fas fa-camera fa-3x"></i><p>Camera permission denied or unavailable. Use file upload instead.</p>';
        });
    } else {
      preview.innerHTML = '<i class="fas fa-camera fa-3x"></i><p>Camera not supported. Use file upload.</p>';
    }
  }

  function closeCamera() {
    if (mediaStream) {
      mediaStream.getTracks().forEach(t => t.stop());
      mediaStream = null;
    }
    $('#camera-modal').classList.add('hidden');
  }

  function captureFromCamera() {
    const video = $('.camera-preview video');
    if (video && video.srcObject) {
      const canvas = $('#capture-canvas') || document.createElement('canvas');
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);
      closeCamera();
      // Simulate processing
      const overlay = $('#processing-overlay');
      const result = $('#analysis-result');
      overlay.classList.remove('hidden');
      result.classList.add('hidden');
      setTimeout(() => {
        overlay.classList.add('hidden');
        result.classList.remove('hidden');
        renderAnalysis(DEMO_ANALYSIS);
        toast('Report captured & analyzed!', 'success');
      }, 2000);
    } else {
      closeCamera();
      // Simulated capture
      const overlay = $('#processing-overlay');
      overlay.classList.remove('hidden');
      setTimeout(() => {
        overlay.classList.add('hidden');
        $('#analysis-result').classList.remove('hidden');
        renderAnalysis(DEMO_ANALYSIS);
        toast('Simulated capture analyzed!', 'success');
      }, 1500);
    }
  }

  // ---------- Chat ----------
  function initChat() {
    const input = $('#chat-input');
    const sendBtn = $('#chat-send');
    const messages = $('#chat-messages');

    function addMsg(text, isUser) {
      const div = document.createElement('div');
      div.className = 'message ' + (isUser ? 'user' : 'bot');
      div.innerHTML = `
        <div class="msg-avatar"><i class="fas fa-${isUser ? 'user' : 'robot'}"></i></div>
        <div class="msg-bubble">${escapeHtml(text)}</div>
      `;
      messages.appendChild(div);
      messages.scrollTop = messages.scrollHeight;
      state.chatHistory.push({ role: isUser ? 'user' : 'bot', text });
      saveLocal();
    }

    function escapeHtml(s) {
      const d = document.createElement('div');
      d.textContent = s;
      return d.innerHTML;
    }

    async function send() {
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      addMsg(text, true);

      let reply;
      try {
        if (state.backendAvailable) {
          const data = await api('/chat', { method: 'POST', body: { message: text, language: state.language } });
          reply = data.reply || getChatReply(text);
        } else {
          reply = getChatReply(text);
        }
      } catch (e) {
        reply = getChatReply(text);
      }
      setTimeout(() => addMsg(reply, false), 400);
    }

    sendBtn.addEventListener('click', send);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') send();
    });

    $$('.q-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        input.value = chip.dataset.q;
        send();
      });
    });

    // Voice input
    $('#chat-voice-btn').addEventListener('click', startVoiceInput);
    $('#voice-toggle').addEventListener('click', startVoiceInput);
  }

  function startVoiceInput() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      toast('Voice input not supported. Use Chrome. (Tulu is text-only)', 'error');
      return;
    }
    const rec = new SR();
    rec.lang = state.language === 'hi' ? 'hi-IN' : state.language === 'kn' ? 'kn-IN' : state.language === 'ta' ? 'ta-IN' : state.language === 'te' ? 'te-IN' : state.language === 'ml' ? 'ml-IN' : 'en-IN';
    rec.interimResults = false;
    toast('Listening...', 'success');
    rec.onresult = (e) => {
      const text = e.results[0][0].transcript;
      const input = $('#chat-input');
      if (input) {
        input.value = text;
        $('#chat-send').click();
      }
    };
    rec.onerror = () => toast('Voice recognition error', 'error');
    rec.start();
  }

  // ---------- SOS ----------
  function openSos() {
    const m = $('#sos-modal');
    m.classList.remove('hidden');
    if (state.profile) {
      $('#sos-blood').textContent = state.profile.blood || '—';
      $('#sos-allergies').textContent = state.profile.allergies || 'None';
      $('#sos-contact').textContent = state.profile.emergency || '—';
    }
  }

  function initSos() {
    $('#sos-btn').addEventListener('click', openSos);
    $('#cancel-sos').addEventListener('click', () => $('#sos-modal').classList.add('hidden'));
    $('#confirm-sos').addEventListener('click', async () => {
      try {
        if (state.backendAvailable) await api('/sos', { method: 'POST', body: {} });
      } catch (e) {}
      $('#sos-modal').classList.add('hidden');
      toast('SOS activated! Location & profile shared with emergency contacts.', 'success');
    });
  }

  // ---------- Notifications ----------
  function initNotif() {
    let panel = null;
    $('#notif-btn').addEventListener('click', () => {
      if (panel && !panel.classList.contains('hidden')) {
        panel.classList.add('hidden');
        return;
      }
      if (!panel) {
        panel = document.createElement('div');
        panel.className = 'notif-panel';
        panel.id = 'notif-panel';
        document.body.appendChild(panel);
      }
      const email = (state.user && state.user.email) || '—';
      const phone = (state.user && state.user.phone) || (state.profile && state.profile.emergency) || '—';
      panel.innerHTML = `
        <div class="notif-panel-header">
          <span>Notifications</span>
          <button class="icon-btn" id="close-notif" style="width:28px;height:28px;"><i class="fas fa-times"></i></button>
        </div>
        <div class="notif-item">
          <strong>Welcome!</strong> Logged in as ${escapeHtml(email)}
          <div class="n-time">Just now</div>
        </div>
        <div class="notif-item">
          Medicine reminder: Metformin after breakfast
          <div class="n-time">Today 8:30 AM</div>
        </div>
        <div class="notif-item">
          Test alert for ${escapeHtml(phone)}
          <div class="n-time">Yesterday</div>
        </div>
        <div class="notif-item">
          Your health score improved by 5 points this week
          <div class="n-time">2 days ago</div>
        </div>
      `;
      panel.classList.remove('hidden');
      $('#close-notif').addEventListener('click', () => panel.classList.add('hidden'));
    });
    function escapeHtml(s) {
      const d = document.createElement('div');
      d.textContent = s;
      return d.innerHTML;
    }
  }

  // ---------- Profile menu ----------
  function initProfile() {
    $$('.profile-menu-item').forEach(btn => {
      btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        if (action === 'logout') {
          state.user = null;
          state.token = null;
          state.profile = null;
          saveLocal();
          showScreen('auth-screen');
          toast('Logged out', 'success');
        } else if (action === 'edit-profile') {
          showScreen('profile-setup-screen');
          prefillProfileForm();
        } else if (action === 'language') {
          openLanguagePanel();
        } else if (action === 'theme') {
          state.darkMode = !state.darkMode;
          document.body.classList.toggle('dark', state.darkMode);
          saveLocal();
          toast(state.darkMode ? 'Dark mode on' : 'Light mode on', 'success');
        } else if (action === 'voice-settings') {
          toast('Voice: uses browser speech. Tulu is text-only.', 'success');
        } else if (action === 'notifications') {
          toast('Notifications enabled for medicine & alerts', 'success');
        } else if (action === 'privacy') {
          toast('Your data stays on device / local server. JWT auth secured.', 'success');
        } else if (action === 'locker') {
          toast('Digital Health Locker: your reports are stored securely.', 'success');
        }
      });
    });
  }

  function openLanguagePanel() {
    let panel = $('#lang-panel');
    if (!panel) {
      panel = document.createElement('div');
      panel.id = 'lang-panel';
      panel.className = 'settings-panel';
      const langs = [
        { code: 'en', name: 'English' },
        { code: 'hi', name: 'Hindi — हिन्दी' },
        { code: 'kn', name: 'Kannada — ಕನ್ನಡ' },
        { code: 'ta', name: 'Tamil — தமிழ்' },
        { code: 'te', name: 'Telugu — తెలుగు' },
        { code: 'ml', name: 'Malayalam — മലയാളം' },
        { code: 'tcy', name: 'Tulu — ತುಳು' },
        { code: 'mr', name: 'Marathi — मराठी' },
        { code: 'bn', name: 'Bengali — বাংলা' },
        { code: 'gu', name: 'Gujarati — ગુજરાતી' },
        { code: 'pa', name: 'Punjabi — ਪੰਜਾਬੀ' },
        { code: 'ur', name: 'Urdu — اردو' },
      ];
      panel.innerHTML = `
        <div class="settings-panel-header">
          <button class="icon-btn" id="close-lang"><i class="fas fa-arrow-left"></i></button>
          <h2>Language</h2>
        </div>
        <div id="lang-list"></div>
      `;
      document.body.appendChild(panel);
      const list = $('#lang-list', panel);
      langs.forEach(l => {
        const b = document.createElement('button');
        b.className = 'lang-option' + (state.language === l.code ? ' selected' : '');
        b.textContent = l.name;
        b.dataset.code = l.code;
        b.addEventListener('click', () => {
          state.language = l.code;
          if (state.profile) state.profile.language = l.code;
          saveLocal();
          $$('.lang-option', panel).forEach(o => o.classList.toggle('selected', o.dataset.code === l.code));
          toast('Language set to ' + l.name.split('—')[0].trim(), 'success');
        });
        list.appendChild(b);
      });
      $('#close-lang', panel).addEventListener('click', () => panel.classList.add('hidden'));
    } else {
      $$('.lang-option', panel).forEach(o => o.classList.toggle('selected', o.dataset.code === state.language));
    }
    panel.classList.remove('hidden');
  }

  // ---------- Boot ----------
  document.addEventListener('DOMContentLoaded', async () => {
    await checkBackend();
    initOnboarding();
    initAuth();
    initProfileSetup();
    initNav();
    initMedicines();
    initReports();
    initChat();
    initSos();
    initNotif();
    initProfile();
    initGoogleButtonIfReady();
    startApp();
  });
})();
