import re

# ─── index.html ───────────────────────────────────────────────────────────────
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add favicon + meta description after the title tag line
FAVICON = (
    '\n  <meta name="description" content="HealthVerse AI: Translate medical reports, '
    'chat with an AI health assistant in English, Hindi, Kannada, Tulu, Tamil, Telugu and more.">'
    '\n  <meta name="theme-color" content="#9b7EBD">'
    '\n  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,'
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
    "%3Crect width='64' height='64' rx='14' fill='%239b7EBD'/%3E"
    "%3Ccircle cx='26' cy='20' r='8' fill='none' stroke='white' stroke-width='4'/%3E"
    "%3Cline x1='26' y1='28' x2='26' y2='42' stroke='white' stroke-width='4' stroke-linecap='round'/%3E"
    "%3Cline x1='26' y1='42' x2='42' y2='42' stroke='white' stroke-width='4' stroke-linecap='round'/%3E"
    "%3Ccircle cx='42' cy='46' r='4' fill='white'/%3E%3C/svg%3E\">"
)

MARKER = '</title>'
if FAVICON not in html:
    html = html.replace(MARKER, MARKER + FAVICON, 1)
    print('✓ favicon + meta added')
else:
    print('  favicon already present')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# ─── styles.css ────────────────────────────────────────────────────────────────
with open('css/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

NEW_CSS = """
/* ========== CHAT HEADER LANGUAGE SWITCHER (additive) ========== */
.chat-header {
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}
.chat-header-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.chat-header-right {
  display: flex;
  align-items: center;
  gap: 6px;
}
.chat-lang-badge {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--primary);
  background: rgba(155, 126, 189, 0.12);
  padding: 2px 8px;
  border-radius: 20px;
  display: inline-block;
}
.chat-lang-select {
  padding: 6px 10px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 0.82rem;
  font-family: inherit;
  color: var(--text);
  background: var(--bg-card);
  cursor: pointer;
  max-width: 120px;
}
.chat-lang-select:focus {
  outline: none;
  border-color: var(--primary);
}

/* ========== WATER / STEPS QUICK-LOG (additive) ========== */
.insight-card-interactive {
  align-items: flex-start;
}
.insight-interactive {
  flex: 1;
}
.insight-interactive p {
  margin-bottom: 6px;
  font-size: 0.88rem;
  line-height: 1.5;
  color: var(--text);
}
.insight-mini-bar {
  height: 6px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}
.insight-mini-fill {
  height: 100%;
  background: linear-gradient(90deg, #42A5F5, #29B6F6);
  border-radius: 4px;
  transition: width 0.5s ease;
}
.insight-mini-fill.steps-fill {
  background: linear-gradient(90deg, #66BB6A, #43A047);
}
.btn-log {
  padding: 5px 12px;
  border-radius: 20px;
  border: 1.5px solid var(--primary);
  background: transparent;
  color: var(--primary);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: var(--transition);
}
.btn-log:hover {
  background: rgba(155, 126, 189, 0.1);
}
.btn-log:active {
  transform: scale(0.97);
}
"""

MARKER_CSS = '/* Responsive */'
if '.chat-lang-badge' not in css:
    css = css.replace(MARKER_CSS, NEW_CSS + MARKER_CSS, 1)
    print('✓ CSS additions applied')
else:
    print('  CSS already patched')

with open('css/styles.css', 'w', encoding='utf-8') as f:
    f.write(css)

# ─── js/app.js ─────────────────────────────────────────────────────────────────
with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 2a. Add Marathi + Bengali AI responses (after ml block)
NEW_AI = """    mr: {
      report: "तुमच्या लॅब रिपोर्टमध्ये उपवास रक्त साखर 118 mg/dL आणि LDL 142 mg/dL आहे. HbA1c 6.2%. मध्यम धोका — आहार, चालणे आणि औषधे सुरू ठेवा.",
      foods: "पांढरा तांदूळ, मिठाई, तळलेले अन्न कमी करा. ज्वारी, बाजरी, भाज्या खा.",
      metformin: "मेटफॉर्मिन टाइप 2 मधुमेहाचे औषध आहे. जेवणासोबत घ्या.",
      rice: "तांदूळ मर्यादित प्रमाणात खाऊ शकता. तपकिरी तांदूळ किंवा ज्वारी चांगले.",
      diabetes: "मधुमेहात रक्तातील साखर जास्त असते. औषधे, आहार, व्यायामाने नियंत्रण ठेवता येते.",
      default: "मी तुमचा HealthVerse AI सहाय्यक आहे. रिपोर्ट, औषधे किंवा आहाराबद्दल विचारा."
    },
    bn: {
      report: "আপনার ল্যাব রিপোর্টে উপবাস রক্তে শর্করা 118 mg/dL এবং LDL 142 mg/dL। HbA1c 6.2%। মাঝারি ঝুঁকি — খাদ্য, হাঁটা এবং ওষুধ চালিয়ে যান।",
      foods: "সাদা ভাত, মিষ্টি, ভাজা খাবার সীমিত করুন। রাগি, সবজি খান।",
      metformin: "মেটফর্মিন টাইপ 2 ডায়াবেটিসের ওষুধ। খাবারের সাথে নিন।",
      rice: "ভাত পরিমিত খাওয়া যেতে পারে। লাল চাল বা রাগি ভালো।",
      diabetes: "ডায়াবেটিসে রক্তে শর্করা বেশি থাকে। ওষুধ, খাদ্য, ব্যায়ামে নিয়ন্ত্রণ করা যায়।",
      default: "আমি আপনার HealthVerse AI সহায়ক। রিপোর্ট, ওষুধ বা খাদ্য সম্পর্কে জিজ্ঞাসা করুন।"
    }
"""

if 'mr:' not in js:
    js = js.replace('  },\n\n  translations:', NEW_AI + '  },\n\n  translations:', 1)
    print('✓ Marathi + Bengali AI responses added')
else:
    print('  mr/bn already present')

# 2b. Bind the chat language switcher + water/steps logger + update badge
NEW_BIND = """
    // ── Chat language switcher (additive) ──────────────────────────
    const chatLangSwitcher = document.getElementById('chat-lang-switcher');
    if (chatLangSwitcher) {
      chatLangSwitcher.value = this.state.chatLang || 'en';
      chatLangSwitcher.addEventListener('change', (e) => {
        this.state.chatLang = e.target.value;
        localStorage.setItem('hv_chat_lang', e.target.value);
        if (this.state.recognition) this.state.recognition.lang = this.speechLangCode(e.target.value);
        this.updateChatLangBadge();
        const langNames = { en:'English', hi:'हिंदी', kn:'ಕನ್ನಡ', tcy:'ತುಳು', ta:'தமிழ்', te:'తెలుగు', ml:'മലയാളം', mr:'मराठी', bn:'বাংলা' };
        this.showToast('AI language: ' + (langNames[e.target.value] || e.target.value));
      });
    }
    this.updateChatLangBadge();

    // ── Water / Steps quick-log (additive) ─────────────────────────
    let waterMl = 1200, stepCount = 5400;
    document.getElementById('log-water-btn')?.addEventListener('click', () => {
      waterMl = Math.min(waterMl + 250, 2500);
      const L = (waterMl / 1000).toFixed(1);
      const el = document.getElementById('water-count');
      if (el) el.textContent = L;
      const bar = document.getElementById('water-bar');
      if (bar) bar.style.width = Math.round((waterMl / 2500) * 100) + '%';
      this.showToast('Water logged: ' + L + ' / 2.5 L');
    });
    document.getElementById('log-steps-btn')?.addEventListener('click', () => {
      stepCount = Math.min(stepCount + 500, 7500);
      const el = document.getElementById('steps-count');
      if (el) el.textContent = stepCount.toLocaleString();
      const bar = document.getElementById('steps-bar');
      if (bar) bar.style.width = Math.round((stepCount / 7500) * 100) + '%';
      this.showToast('Steps logged: ' + stepCount.toLocaleString() + ' / 7,500');
    });
"""

if 'log-water-btn' not in js:
    js = js.replace("    document.getElementById('forgot-password')", NEW_BIND + "    document.getElementById('forgot-password')", 1)
    print('✓ Chat-lang switcher + water/steps binders added')
else:
    print('  log-water already bound')

# 2c. Add updateChatLangBadge helper method before the last closing }
BADGE_METHOD = """
  updateChatLangBadge() {
    const badge = document.getElementById('chat-lang-badge');
    const switcher = document.getElementById('chat-lang-switcher');
    const langNames = { en:'English', hi:'हिंदी', kn:'ಕನ್ನಡ', tcy:'ತுಳು', ta:'தமிழ்', te:'తెలుగు', ml:'മലయാളം', mr:'मराठी', bn:'বাংলা' };
    const lang = this.state.chatLang || 'en';
    if (badge) badge.textContent = '🌐 ' + (langNames[lang] || lang);
    if (switcher && switcher.value !== lang) switcher.value = lang;
  },

"""

if 'updateChatLangBadge' not in js:
    js = js.replace('  showToast(msg) {', BADGE_METHOD + '  showToast(msg) {', 1)
    print('✓ updateChatLangBadge helper added')
else:
    print('  helper already present')

# 2d. Call updateChatLangBadge whenever switchView('chat') runs
if "switchView('chat') this.updateChatLangBadge" not in js:
    js = js.replace(
        "    document.querySelectorAll('.quick-btn').forEach(btn => {\n      btn.addEventListener('click', (e) => {\n        const action = e.currentTarget.dataset.action;\n        if (action === 'upload') this.switchView('reports');\n        else if (action === 'chat') this.switchView('chat');",
        "    document.querySelectorAll('.quick-btn').forEach(btn => {\n      btn.addEventListener('click', (e) => {\n        const action = e.currentTarget.dataset.action;\n        if (action === 'upload') this.switchView('reports');\n        else if (action === 'chat') { this.switchView('chat'); this.updateChatLangBadge(); }",
        1
    )
    print('✓ badge refresh on chat open hooked')
else:
    print('  badge refresh already hooked')

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print('\nAll patches applied successfully.')
