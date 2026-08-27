"""
HealthVerse AI — Simulated OCR / analysis / chat / translation
Ready to swap for Gemini / OpenAI / Google Vision.
"""

DEMO_ANALYSIS = {
    "summary": (
        "Based on the uploaded lab report, most values are within normal range. "
        "Slight elevation in fasting blood sugar and LDL cholesterol noted. "
        "Continue current medication and lifestyle changes."
    ),
    "risk": "moderate",
    "findings": [
        {"text": "Fasting Blood Sugar: 118 mg/dL (Slightly High)", "abnormal": True},
        {"text": "HbA1c: 6.2% (Near normal)", "abnormal": False},
        {"text": "LDL Cholesterol: 142 mg/dL (Borderline High)", "abnormal": True},
        {"text": "Hemoglobin: 13.8 g/dL (Normal)", "abnormal": False},
        {"text": "Creatinine: 0.9 mg/dL (Normal)", "abnormal": False},
    ],
    "details": [
        {"param": "Fasting Glucose", "value": "118 mg/dL", "ref": "70-100", "status": "High"},
        {"param": "HbA1c", "value": "6.2%", "ref": "<5.7%", "status": "Elevated"},
        {"param": "Total Cholesterol", "value": "210 mg/dL", "ref": "<200", "status": "Borderline"},
        {"param": "LDL", "value": "142 mg/dL", "ref": "<100", "status": "High"},
        {"param": "HDL", "value": "48 mg/dL", "ref": ">40", "status": "Normal"},
        {"param": "Triglycerides", "value": "145 mg/dL", "ref": "<150", "status": "Normal"},
        {"param": "Hemoglobin", "value": "13.8 g/dL", "ref": "12-16", "status": "Normal"},
        {"param": "Creatinine", "value": "0.9 mg/dL", "ref": "0.6-1.2", "status": "Normal"},
    ],
    "medicines": [
        {
            "name": "Metformin 500 mg",
            "dosage": "1 tablet twice daily after meals",
            "purpose": "Controls blood sugar levels in type 2 diabetes",
            "side": "Nausea, diarrhea (usually temporary)",
        },
        {
            "name": "Amlodipine 5 mg",
            "dosage": "1 tablet once daily",
            "purpose": "Lowers blood pressure",
            "side": "Ankle swelling, dizziness",
        },
        {
            "name": "Atorvastatin 10 mg",
            "dosage": "1 tablet at night",
            "purpose": "Reduces cholesterol",
            "side": "Muscle pain (rare)",
        },
    ],
}

TRANSLATIONS = {
    "hi": {
        "summary": "अपलोड की गई लैब रिपोर्ट के आधार पर, अधिकांश मान सामान्य सीमा में हैं। उपवास रक्त शर्करा और एलडीएल कोलेस्ट्रॉल में थोड़ी वृद्धि देखी गई। वर्तमान दवा और जीवनशैली परिवर्तन जारी रखें।",
    },
    "kn": {
        "summary": "ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಲ್ಯಾಬ್ ರಿಪೋರ್ಟ್ ಆಧಾರದ ಮೇಲೆ, ಹೆಚ್ಚಿನ ಮೌಲ್ಯಗಳು ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಯಲ್ಲಿವೆ. ಉಪವಾಸ ರಕ್ತದ ಸಕ್ಕರೆ ಮತ್ತು LDL ಕೊಲೆಸ್ಟ್ರಾಲ್‌ನಲ್ಲಿ ಸ್ವಲ್ಪ ಏರಿಕೆ ಕಂಡುಬಂದಿದೆ.",
    },
    "ta": {
        "summary": "பதிவேற்றப்பட்ட ஆய்வக அறிக்கையின் அடிப்படையில், பெரும்பாலான மதிப்புகள் இயல்பான வரம்பில் உள்ளன. உண்ணாவிரத இரத்த சர்க்கரை மற்றும் LDL கொலஸ்ட்ரால் சற்று உயர்ந்துள்ளது.",
    },
    "te": {
        "summary": "అప్‌లోడ్ చేసిన ల్యాబ్ రిపోర్ట్ ఆధారంగా, చాలా విలువలు సాధారణ పరిధిలో ఉన్నాయి. ఉపవాస రక్త చక్కెర మరియు LDL కొలెస్ట్రాల్‌లో కొద్దిగా పెరుగుదల కనిపించింది.",
    },
    "ml": {
        "summary": "അപ്‌ലോഡ് ചെയ്ത ലാബ് റിപ്പോർട്ട് അടിസ്ഥാനമാക്കി, മിക്ക മൂല്യങ്ങളും സാധാരണ പരിധിയിലാണ്. ഉപവാസ രക്തത്തിലെ പഞ്ചസാരയിലും LDL കൊളസ്ട്രോളിലും ചെറിയ വർദ്ധനവ് കാണുന്നു.",
    },
    "tcy": {
        "summary": "ಅಪ್‌ಲೋಡ್ ಮಲ್ಪಿನ ಲ್ಯಾಬ್ ರಿಪೋರ್ಟ್‌ದ ಅಡಿಟ್, ಬಹುತೇಕ ಮೌಲ್ಯೊಲು ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಡ್ ಉಂಡು. ಉಪವಾಸ ರಕ್ತದ ಸಕ್ಕರೆ ಬೊಕ್ಕ LDL ಕೊಲೆಸ್ಟ್ರಾಲ್‌ಡ್ ಸ್ವಲ್ಪ ಏರಿಕೆ ತೋಜುಂಡು.",
    },
}

CHAT = {
    "en": {
        "default": "I'm your HealthVerse AI assistant. Based on your profile, continue medications, walk 30 min daily, and monitor blood sugar. How else can I help?",
        "report": "Your report shows fasting glucose slightly elevated at 118 mg/dL and LDL at 142. Most other parameters are normal.",
        "food": "Prefer whole grains, millets, leafy greens. Limit sweets, fried food, and white rice.",
        "metformin": "Metformin 500mg helps control blood sugar. Take after meals. Mild nausea may occur temporarily.",
        "rice": "Small portions of brown rice or millets are fine. Prefer whole grains over white rice.",
    },
    "hi": {
        "default": "मैं आपका HealthVerse AI सहायक हूँ। दवाएँ जारी रखें, रोज़ 30 मिनट पैदल चलें। और कैसे मदद करूँ?",
        "report": "आपकी रिपोर्ट में फास्टिंग शुगर 118 और LDL 142 थोड़ा बढ़ा है। बाकी ज्यादातर मान सामान्य हैं।",
        "food": "साबुत अनाज, बाजरा, हरी सब्जियाँ लें। मिठाई और तला कम करें।",
        "metformin": "मेटफॉर्मिन 500mg शुगर कंट्रोल करता है। भोजन के बाद लें।",
        "rice": "थोड़ा ब्राउन राइस या बाजरा खा सकते हैं।",
    },
    "kn": {
        "default": "ನಾನು ನಿಮ್ಮ HealthVerse AI ಸಹಾಯಕ. ಔಷಧಿ ಮುಂದುವರಿಸಿ, ದಿನಕ್ಕೆ 30 ನಿಮಿಷ ನಡೆಯಿರಿ.",
        "report": "ಉಪವಾಸ ಸಕ್ಕರೆ 118 ಮತ್ತು LDL 142 ಸ್ವಲ್ಪ ಹೆಚ್ಚು. ಉಳಿದವು ಸಾಮಾನ್ಯ.",
        "food": "ಸಂಪೂರ್ಣ ಧಾನ್ಯ, ರಾಗಿ, ಹಸಿರು ತರಕಾರಿ ತೆಗೆದುಕೊಳ್ಳಿ.",
        "metformin": "ಮೆಟ್‌ಫಾರ್ಮಿನ್ 500mg ಸಕ್ಕರೆ ನಿಯಂತ್ರಿಸುತ್ತದೆ. ಊಟದ ನಂತರ ತೆಗೆದುಕೊಳ್ಳಿ.",
        "rice": "ಸ್ವಲ್ಪ ಕಂದು ಅನ್ನ ಅಥವಾ ರಾಗಿ ತಿನ್ನಬಹುದು.",
    },
}


def analyze_report(filename: str = None) -> dict:
    """Simulate OCR + AI analysis."""
    return dict(DEMO_ANALYSIS)


def translate_summary(analysis: dict, lang: str) -> dict:
    t = TRANSLATIONS.get(lang)
    if not t:
        return analysis
    out = dict(analysis)
    out["summary"] = t.get("summary", analysis.get("summary"))
    return out


def chat_reply(message: str, language: str = "en") -> str:
    lang = language if language in CHAT else "en"
    replies = CHAT[lang]
    m = (message or "").lower()
    if any(k in m for k in ("report", "explain", "रिपोर्ट", "ರಿಪೋರ್ಟ್")):
        return replies["report"]
    if any(k in m for k in ("food", "avoid", "खाना", "ಆಹಾರ")):
        return replies["food"]
    if "metformin" in m or "मेट" in m or "ಮೆಟ್" in m:
        return replies["metformin"]
    if any(k in m for k in ("rice", "चावल", "ಅನ್ನ")):
        return replies["rice"]
    return replies["default"]
