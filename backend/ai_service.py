"""
HealthVerse AI — Multilingual AI Healthcare Assistant & Medical Service
Strictly follows the Multilingual Response System Prompt guidelines.
"""
import re
import random
from datetime import datetime

# ── Sample lab analysis (used when a report is uploaded) ──────────
SAMPLE_ANALYSIS = {
    "summary": (
        "Based on the uploaded lab report, most values are within normal range. "
        "Slight elevation in fasting blood sugar and LDL cholesterol noted. "
        "Continue current medication and lifestyle changes."
    ),
    "risk_level": "moderate",
    "findings": [
        {"parameter": "Fasting Blood Sugar", "value": "118 mg/dL", "reference": "70-100", "status": "high", "note": "Slightly elevated"},
        {"parameter": "HbA1c", "value": "6.2%", "reference": "<5.7%", "status": "elevated", "note": "Near pre-diabetic range"},
        {"parameter": "Total Cholesterol", "value": "210 mg/dL", "reference": "<200", "status": "borderline", "note": ""},
        {"parameter": "LDL Cholesterol", "value": "142 mg/dL", "reference": "<100", "status": "high", "note": "Borderline high"},
        {"parameter": "HDL Cholesterol", "value": "48 mg/dL", "reference": ">40", "status": "normal", "note": ""},
        {"parameter": "Triglycerides", "value": "145 mg/dL", "reference": "<150", "status": "normal", "note": ""},
        {"parameter": "Hemoglobin", "value": "13.8 g/dL", "reference": "12-16", "status": "normal", "note": ""},
        {"parameter": "Creatinine", "value": "0.9 mg/dL", "reference": "0.6-1.2", "status": "normal", "note": ""},
    ],
    "medicines": [
        {
            "name": "Metformin 500 mg",
            "dosage": "1 tablet twice daily after meals",
            "purpose": "Controls blood sugar levels in type 2 diabetes",
            "side_effects": "Nausea, diarrhea (usually temporary)"
        },
        {
            "name": "Amlodipine 5 mg",
            "dosage": "1 tablet once daily",
            "purpose": "Lowers blood pressure",
            "side_effects": "Ankle swelling, dizziness"
        },
        {
            "name": "Atorvastatin 10 mg",
            "dosage": "1 tablet at night",
            "purpose": "Reduces cholesterol",
            "side_effects": "Muscle pain (rare)"
        },
    ],
    "recommendations": {
        "diet": [
            "Prefer whole grains and millets over white rice",
            "Include leafy greens and fiber-rich foods",
            "Limit sweets, fried items and processed food",
            "Small frequent meals recommended"
        ],
        "exercise": [
            "30–45 min brisk walk daily",
            "Light yoga or stretching in the morning",
            "Avoid heavy lifting if blood pressure is high"
        ],
        "warnings": [
            "Sudden dizziness or chest pain — seek emergency care",
            "Excessive thirst or frequent urination",
            "Unexplained fatigue or blurred vision"
        ],
        "lifestyle": [
            "Sleep 7–8 hours every night",
            "Stay hydrated — aim for 2.5 L water daily",
            "Monitor blood sugar regularly"
        ]
    },
    "diagnoses": ["Prediabetes / Early Type 2 Diabetes risk", "Dyslipidemia (borderline)"],
}

TRANSLATIONS = {
    "hi": {
        "summary": "अपलोड की गई लैब रिपोर्ट के आधार पर, अधिकांश मूल्य सामान्य सीमा में हैं। उपवास रक्त शर्करा और एलडीएल कोलेस्ट्रॉल में थोड़ी वृद्धि देखी गई। वर्तमान दवा और जीवनशैली में बदलाव जारी रखें।",
        "findings": [
            "उपवास रक्त शर्करा: 118 mg/dL (थोड़ा उच्च)",
            "HbA1c: 6.2% (लगभग सामान्य)",
            "एलडीएल कोलेस्ट्रॉल: 142 mg/dL (सीमा रेखा उच्च)",
            "हीमोग्लोबिन: 13.8 g/dL (सामान्य)",
            "क्रिएटिनिन: 0.9 mg/dL (सामान्य)"
        ]
    },
    "kn": {
        "summary": "ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಲ್ಯಾಬ್ ವರದಿಯ ಆಧಾರದ ಮೇಲೆ, ಹೆಚ್ಚಿನ ಮೌಲ್ಯಗಳು ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಯಲ್ಲಿವೆ. ಉಪವಾಸ ರಕ್ತದ ಸಕ್ಕರೆ ಮತ್ತು LDL ಕೊಲೆಸ್ಟ್ರಾಲ್‌ನಲ್ಲಿ ಸ್ವಲ್ಪ ಏರಿಕೆ ಕಂಡುಬಂದಿದೆ. ಪ್ರಸ್ತುತ ಔಷಧಿ ಮತ್ತು ಜೀವನಶೈಲಿ ಬದಲಾವಣೆಗಳನ್ನು ಮುಂದುವರಿಸಿ.",
        "findings": [
            "ಉಪವಾಸ ರಕ್ತದ ಸಕ್ಕರೆ: 118 mg/dL (ಸ್ವಲ್ಪ ಹೆಚ್ಚು)",
            "HbA1c: 6.2% (ಸಾಮಾನ್ಯಕ್ಕೆ ಹತ್ತಿರ)",
            "LDL ಕೊಲೆಸ್ಟ್ರಾಲ್: 142 mg/dL (ಸೀಮಾರೇಖೆ ಹೆಚ್ಚು)",
            "ಹಿಮೋಗ್ಲೋಬಿನ್: 13.8 g/dL (ಸಾಮಾನ್ಯ)",
            "ಕ್ರಿಯೇಟಿನಿನ್: 0.9 mg/dL (ಸಾಮಾನ್ಯ)"
        ]
    },
    "ta": {
        "summary": "பதிவேற்றப்பட்ட ஆய்வக அறிக்கையின் அடிப்படையில், பெரும்பாலான மதிப்புகள் இயல்பான வரம்பில் உள்ளன. உண்ணாவிரத இரத்த சர்க்கரை மற்றும் LDL கொழுப்பில் சிறிது உயர்வு காணப்படுகிறது. தற்போதைய மருந்து மற்றும் வாழ்க்கைமுறை மாற்றங்களைத் தொடரவும்.",
        "findings": [
            "உண்ணாவிரத இரத்த சர்க்கரை: 118 mg/dL (சற்றே அதிகம்)",
            "HbA1c: 6.2% (இயல்பிற்கு அருகில்)",
            "LDL கொழுப்பு: 142 mg/dL (எல்லைக்கோடு அதிகம்)",
            "ஹீமோகுளோபின்: 13.8 g/dL (இயல்பு)",
            "கிரியேட்டினின்: 0.9 mg/dL (இயல்பு)"
        ]
    },
    "te": {
        "summary": "అప్‌లోడ్ చేసిన ల్యాబ్ రిపోర్ట్ ఆధారంగా, చాలా విలువలు సాధారణ పరిధిలో ఉన్నాయి. ఉపవాస రక్త చక్కెర మరియు LDL కొలెస్ట్రాల్‌లో కొంచెం పెరుగుదల కనిపించింది. ప్రస్తుత మందులు మరియు జీవనశైలి మార్పులను కొనసాగించండి.",
        "findings": [
            "ఉపవాస రక్త చక్కెర: 118 mg/dL (కొంచెం ఎక్కువ)",
            "HbA1c: 6.2% (సాధారణానికి దగ్గరగా)",
            "LDL కొలెస్ట్రాల్: 142 mg/dL (సరిహద్దు ఎక్కువ)",
            "హిమోగ్లోబిన్: 13.8 g/dL (సాధారణం)",
            "క్రియేటినిన్: 0.9 mg/dL (సాధారణం)"
        ]
    },
    "ml": {
        "summary": "അപ്‌ലോഡ് ചെയ്ത ലാബ് റിപ്പോർട്ടിന്റെ അടിസ്ഥാനത്തിൽ, മിക്ക മൂല്യങ്ങളും സാധാരണ പരിധിയിലാണ്. ഉപവാസ രക്തത്തിലെ പഞ്ചസാരയും LDL കൊളസ്ട്രോളും ചെറുതായി ഉയർന്നതായി കണ്ടെത്തി. നിലവിലെ മരുന്നും ജീവിതശൈലി മാറ്റങ്ങളും തുടരുക.",
        "findings": [
            "ഉപവാസ രക്തത്തിലെ പഞ്ചസാര: 118 mg/dL (ചെറുതായി ഉയർന്നത്)",
            "HbA1c: 6.2% (സാധാരണയോട് അടുത്ത്)",
            "LDL കൊളസ്ട്രോൾ: 142 mg/dL (അതിർത്തി ഉയർന്നത്)",
            "ഹീമോഗ്ലോബിൻ: 13.8 g/dL (സാധാരണം)",
            "ക്രിയേറ്റിനിൻ: 0.9 mg/dL (സാധാരണം)"
        ]
    },
    "tcy": {
        "summary": "ಅಪ್‌ಲೋಡ್ ಮಲ್ತಿನ ಲ್ಯಾಬ್ ರಿಪೋರ್ಟ್‌ದ ಆಧಾರೊಡು, ಮಸ್ತ್ ಮೌಲ್ಯೊಲು ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಡ್ ಉಂಡು. ಉಪವಾಸ ರಕ್ತದ ಸಕ್ಕರೆ ಬೊಕ್ಕ LDL ಕೊಲೆಸ್ಟ್ರಾಲ್‌ಡ್ ಸ್ವಲ್ಪ ಏರಿಕೆ ತೋಜುಂಡು. ಪ್ರಸ್ತುತ ಮರ್ದ್ ಬೊಕ್ಕ ಜೀವನಶೈಲಿ ಬದಲಾವಣೆ ಮುಂದುವರಿಸಲೆ.",
        "findings": [
            "ಉಪವಾಸ ರಕ್ತದ ಸಕ್ಕರೆ: 118 mg/dL (ಸ್ವಲ್ಪ ಜಾಸ್ತಿ)",
            "HbA1c: 6.2% (ಸಾಮಾನ್ಯೊಗು ಕೈತಲ್)",
            "LDL ಕೊಲೆಸ್ಟ್ರಾಲ್: 142 mg/dL (ಸೀಮಾರೇಖೆ ಜಾಸ್ತಿ)",
            "ಹಿಮೋಗ್ಲೋಬಿನ್: 13.8 g/dL (ಸಾಮಾನ್ಯ)",
            "ಕ್ರಿಯೇಟಿನಿನ್: 0.9 mg/dL (ಸಾಮಾನ್ಯ)"
        ]
    },
    "mr": {
        "summary": "अपलोड केलेल्या लॅब रिपोर्टनुसार, बहुतेक मूल्ये सामान्य श्रेणीत आहेत. फास्टिंग ब्लड शुगर आणि LDL कोलेस्ट्रॉलमध्ये थोडी वाढ दिसून आली आहे. सध्याची औषधे आणि जीवनशैलीतील बदल सुरु ठेवा.",
        "findings": [
            "फास्टिंग ब्लड शुगर: 118 mg/dL (थोडी जास्त)",
            "HbA1c: 6.2% (सामान्य पातळी जवळ)",
            "LDL कोलेस्ट्रॉल: 142 mg/dL (सीमा ओलांडली)",
            "हिमोग्लोबिन: 13.8 g/dL (सामान्य)",
            "क्रिएटिनिन: 0.9 mg/dL (सामान्य)"
        ]
    }
}


# ── Language Detection Helper ────────────────────────────────────
def detect_language(text: str, default_lang: str = "en") -> str:
    """
    Dynamically detect language of the user's latest message based on Unicode ranges & script keywords.
    """
    if not text:
        return default_lang
    
    # 1. Kannada script: \u0C80 - \u0CFF
    if re.search(r'[\u0C80-\u0CFF]', text):
        # Check if Tulu specific vocabulary is present in Kannada script
        if re.search(r'(ಇರೆಗ್|ಉಂಡು|ತೋಜುಂಡು|ಮಲ್ಪುಲೆ|ಎಡ್ಡೆ|ಮರ್ದ್|ತಿನೊಲಿ|ಕೇನ್‌ಲೆ|ಯಾನ್)', text):
            return "tcy"
        return "kn"

    # 2. Devanagari script: \u0900 - \u097F
    if re.search(r'[\u0900-\u097F]', text):
        # Check if Marathi specific words are present
        if re.search(r'(मला|ताप|काय|करावे|नाही|आहे|रक्तदाब|औषध|नमस्कार|करा|जा)', text):
            return "mr"
        return "hi"

    # 3. Tamil script: \u0B80 - \u0BFF
    if re.search(r'[\u0B80-\u0BFF]', text):
        return "ta"

    # 4. Telugu script: \u0C00 - \u0C7F
    if re.search(r'[\u0C00-\u0C7F]', text):
        return "te"

    # 5. Malayalam script: \u0D00 - \u0D7F
    if re.search(r'[\u0D00-\u0D7F]', text):
        return "ml"

    # 6. Bengali script: \u0980 - \u09FF
    if re.search(r'[\u0980-\u09FF]', text):
        return "bn"

    # 7. Transliterated / Romanized keywords
    lower = text.lower()
    if re.search(r'\b(jwara|jvara|namaskara|yenu|madabeku|oushadhi|neeru|kannada)\b', lower):
        return "kn"
    if re.search(r'\b(bukhar|namaste|kya|karun|karoon|dawa|paani|hindi)\b', lower):
        return "hi"
    if re.search(r'\b(kaichal|vanakkam|ennu|marundhu|thanneer|tamil)\b', lower):
        return "ta"
    if re.search(r'\b(jwaram|namaskaram|kavali|mandulu|neellu|telugu)\b', lower):
        return "te"
    if re.search(r'\b(pani|namaskaram|marunnu|vellam|malayalam)\b', lower):
        return "ml"
    if re.search(r'\b(tap|namaskar|kay|karave|aushadh|pani|marathi)\b', lower):
        return "mr"
    if re.search(r'\b(tulu|tcy|yenk|kene|marnd)\b', lower):
        return "tcy"

    return default_lang


# ── Multilingual Responses (Strictly formatted per prompt) ────────
RESPONSES_BY_LANG = {
    "kn": {
        "fever": (
            "ನಿಮಗೆ ಜ್ವರ ಇದ್ದರೆ:\n"
            "• ಸಾಕಷ್ಟು ನೀರು ಕುಡಿಯಿರಿ.\n"
            "• ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ.\n"
            "• ಜ್ವರ ಹೆಚ್ಚು ಇದ್ದರೆ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.\n"
            "• ಉಸಿರಾಟದ ತೊಂದರೆ ಅಥವಾ ತೀವ್ರ ಲಕ್ಷಣಗಳಿದ್ದರೆ ತಕ್ಷಣ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿ."
        ),
        "diabetes": (
            "Diabetes (ಪ್ರಮೇಹ) ನಿಯಂತ್ರಣಕ್ಕೆ:\n"
            "• Blood Sugar ಮಟ್ಟವನ್ನು ನಿಯಮಿತವಾಗಿ ಪರಿಶೀಲಿಸಿ.\n"
            "• ಬಿಳಿ ಅಕ್ಕಿ, ಸಿಹಿ ಮತ್ತು Processed Foods ಸೇವನೆ ಕಡಿಮೆ ಮಾಡಿ.\n"
            "• ದಿನವೂ 30-45 ನಿಮಿಷ Brisk Walking ಮಾಡಿ.\n"
            "• Metformin ಮತ್ತು ಇತರ ಔಷಧಿಗಳನ್ನು ಸಮಯಕ್ಕೆ ಸರಿಯಾಗಿ ತೆಗೆದುಕೊಳ್ಳಿ."
        ),
        "bp": (
            "Blood Pressure (ರಕ್ತದೊತ್ತಡ) ನಿಯಂತ್ರಿಸಲು:\n"
            "• ಆಹಾರದಲ್ಲಿ ಉಪ್ಪಿನ (Salt) ಪ್ರಮಾಣವನ್ನು ಕಡಿಮೆ ಮಾಡಿ.\n"
            "• ದಿನವೂ 30 ನಿಮಿಷಗಳ ಕಾಲ ಲಘು ವ್ಯಾಯಾಮ ಮಾಡಿ.\n"
            "• ಒತ್ತಡವನ್ನು (Stress) ನಿರ್ವಹಿಸಲು ಧ್ಯಾನ ಅಥವಾ ಯೋಗ ಮಾಡಿ.\n"
            "• ವೈದ್ಯರು ಸೂಚಿಸಿದ Amlodipine ನಂತಹ ಔಷಧಿಗಳನ್ನು ತಪ್ಪದೇ ಸೇವಿಸಿ."
        ),
        "report": (
            "ನಿಮ್ಮ ಲ್ಯಾಬ್ ವರದಿಯ ವಿವರಣೆ:\n"
            "• Fasting Blood Sugar: 118 mg/dL (ಸ್ವಲ್ಪ ಹೆಚ್ಚು)\n"
            "• LDL Cholesterol: 142 mg/dL (ಸೀಮಾರೇಖೆ ಗಿಂತ ಹೆಚ್ಚು)\n"
            "• HbA1c: 6.2% (Pre-diabetes ವ್ಯಾಪ್ತಿಗೆ ಹತ್ತಿರ)\n"
            "• Kidney Function ಮತ್ತು Hemoglobin ಮಟ್ಟ ಸಾಮಾನ್ಯವಾಗಿದೆ.\n"
            "• ಆಹಾರ ನಿಯಂತ್ರಣ ಮತ್ತು ದಿನನಿತ್ಯದ ನಡಿಗೆಗೆ ಗಮನ ಕೊಡಿ."
        ),
        "foods": (
            "ಆಹಾರದಲ್ಲಿ ಗಮನಿಸಬೇಕಾದ ಅಂಶಗಳು:\n"
            "• ಬಿಳಿ ಅಕ್ಕಿ, ಸಿಹಿತಿಂಡಿ ಮತ್ತು ಕರಿದ ಪದಾರ್ಥಗಳನ್ನು ಕಡಿಮೆ ಮಾಡಿ.\n"
            "• ರಾಗಿ, ಜೋಳ, ಸಿರಿಧಾನ್ಯಗಳು (Millets) ಮತ್ತು ಹಸಿರು ತರಕಾರಿಗಳನ್ನು ಸೇವಿಸಿ.\n"
            "• ಪ್ರೋಟೀನ್ ಯುಕ್ತ ಆಹಾರ ಹಾಗೂ ನಾರಿನಂಶ (Fiber) ಹೆಚ್ಚಿರುವ ಆಹಾರ ಸೇವಿಸಿ."
        ),
        "metformin": (
            "Metformin ಕುರಿತು ವಿವರ:\n"
            "• Metformin ಅನ್ನು Type 2 Diabetes ನಿಯಂತ್ರಣಕ್ಕೆ ನೀಡಲಾಗುತ್ತದೆ.\n"
            "• ಇದು ಲಿವರ್‌ನಲ್ಲಿ ರಕ್ತದ ಸಕ್ಕರೆ ಉತ್ಪಾದನೆಯನ್ನು ಕಡಿಮೆ ಮಾಡುತ್ತದೆ.\n"
            "• ಔಷಧಿಯನ್ನು ಊಟದ ನಂತರ ತೆಗೆದುಕೊಳ್ಳಿ.\n"
            "• ತೀವ್ರ ವಾಕರಿಕೆ ಅಥವಾ ಆಯಾಸವಿದ್ದರೆ ವೈದ್ಯರ ಗಮನಕ್ಕೆ ತನ್ನಿ."
        ),
        "water": (
            "ನೀರು ಕುಡಿಯುವ ಕುರಿತು:\n"
            "• ದಿನಕ್ಕೆ ಕನಿಷ್ಠ 2.5 ರಿಂದ 3 ಲೀಟರ್ ನೀರು ಕುಡಿಯಿರಿ.\n"
            "• ಬೆಳಿಗ್ಗೆ ಖಾಲಿ ಹೊಟ್ಟೆಯಲ್ಲಿ ಉಗುರುಬೆಚ್ಚಗಿನ ನೀರು ಸೇವಿಸುವುದು ಒಳ್ಳೆಯದು."
        ),
        "greeting": (
            "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ HealthVerse AI ವೈದ್ಯಕೀಯ ಸಹಾಯಕ.\n"
            "• ನಿಮ್ಮ ಲ್ಯಾಬ್ ವರದಿಗಳು\n"
            "• ಔಷಧಿಗಳ ಮಾಹಿತಿ (Metformin, Amlodipine ಇತ್ಯಾದಿ)\n"
            "• ಆಹಾರ ಮತ್ತು ವ್ಯಾಯಾಮದ ಸಲಹೆಗಳು\n"
            "ನೀವು ಯಾವುದರ ಬಗ್ಗೆ ಕೇಳಲು ಬಯಸುತ್ತೀರಿ?"
        ),
        "thanks": (
            "ಧನ್ಯವಾದಗಳು! ನಿಮ್ಮ ಆರೋಗ್ಯದ ಕಾಳಜಿ ವಹಿಸಿ.\n"
            "• ಯಾವುದೇ ಸಂಶಯವಿದ್ದರೂ ಮತ್ತೆ ಕೇಳಬಹುದು."
        ),
        "default": (
            "ನಾನು ನಿಮ್ಮ HealthVerse AI ಸಹಾಯಕ. ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿದ್ದೇನೆ:\n"
            "• ನಿಮ್ಮ ವರದಿಗಳ (Reports) ಅರ್ಥ ತಿಳಿಯಲು\n"
            "• Diabetes, BP ಮತ್ತು ಇತರ ಲಕ್ಷಣಗಳ ಬಗ್ಗೆ ತಿಳಿಯಲು\n"
            "• ಆಹಾರ ಮತ್ತು ಔಷಧಿಗಳ ಕುರಿತು ಮಾಹಿತಿ ಪಡೆಯಲು"
        )
    },
    "hi": {
        "fever": (
            "यदि आपको बुखार है:\n"
            "• पर्याप्त पानी पिएँ।\n"
            "• आराम करें।\n"
            "• यदि तेज बुखार हो तो डॉक्टर से संपर्क करें।\n"
            "• सांस लेने में तकलीफ़ या गंभीर लक्षण हों तो तुरंत अस्पताल जाएँ।"
        ),
        "diabetes": (
            "Diabetes नियंत्रित करने के लिए:\n"
            "• अपने Blood Sugar के स्तर की नियमित जाँच करें।\n"
            "• सफेद चावल, मिठाइयाँ और Processed Foods कम करें।\n"
            "• रोजाना 30-45 मिनट Brisk Walking करें।\n"
            "• डॉक्टर द्वारा बताई गई Metformin और अन्य दवाएँ समय पर लें।"
        ),
        "bp": (
            "Blood Pressure नियंत्रित रखने के लिए:\n"
            "• भोजन में नमक (Salt) की मात्रा कम करें।\n"
            "• प्रतिदिन 30 मिनट का हल्का व्यायाम करें।\n"
            "• तनाव (Stress) कम करने के लिए ध्यान या योग करें।\n"
            "• समय पर डॉक्टर की बताई Amlodipine जैसी दवाएँ लें।"
        ),
        "report": (
            "आपकी लैब रिपोर्ट का विवरण:\n"
            "• Fasting Blood Sugar: 118 mg/dL (थोड़ा उच्च)\n"
            "• LDL Cholesterol: 142 mg/dL (सीमा रेखा पर)\n"
            "• HbA1c: 6.2% (Pre-diabetes श्रेणी के पास)\n"
            "• Kidney Function और Hemoglobin सामान्य हैं।\n"
            "• आहार और पैदल चलने पर ध्यान दें।"
        ),
        "foods": (
            "आहार संबंधी सुझाव:\n"
            "• सफेद चावल, मिठाई और तले हुए खाने से परहेज़ करें।\n"
            "• बाजरा, रागी, साबुत अनाज और हरी सब्जियाँ खाएँ।\n"
            "• पर्याप्त फाइबर और प्रोटीन युक्त भोजन लें।"
        ),
        "metformin": (
            "Metformin के बारे में जानकारी:\n"
            "• Metformin का उपयोग Type 2 Diabetes के इलाज में होता है।\n"
            "• यह लिवर में ग्लूकोज के निर्माण को कम करती है।\n"
            "• इसे भोजन के बाद लें।\n"
            "• यदि उल्टी या पेट में परेशानी हो तो डॉक्टर से सलाह लें।"
        ),
        "water": (
            "पानी पीने के सुझाव:\n"
            "• रोजाना कम से कम 2.5 से 3 लीटर पानी पिएँ।\n"
            "• सुबह गुनगुना पानी पीना बहुत फायदेमंद होता है।"
        ),
        "greeting": (
            "नमस्ते! मैं आपका HealthVerse AI मेडिकल सहायक हूँ।\n"
            "• अपनी लैब रिपोर्ट समझाएँ\n"
            "• दवाओं की जानकारी (Metformin, Amlodipine आदि)\n"
            "• आहार और व्यायाम की सलाह लें\n"
            "मैं आपकी क्या मदद कर सकता हूँ?"
        ),
        "thanks": (
            "धन्यवाद! अपनी सेहत का ख्याल रखें।\n"
            "• किसी भी स्वास्थ्य संबंधी सवाल के लिए बेझिझक पूछें।"
        ),
        "default": (
            "मैं आपका HealthVerse AI सहायक हूँ। मैं आपकी सहायता कर सकता हूँ:\n"
            "• अपनी रिपोर्ट का विश्लेषण पाने में\n"
            "• Diabetes, Blood Pressure या लक्षणों के बारे में जानने में\n"
            "• सही आहार और दवा की सलाह पाने में"
        )
    },
    "en": {
        "fever": (
            "If you have a fever:\n"
            "• Stay hydrated.\n"
            "• Get enough rest.\n"
            "• Monitor your temperature.\n"
            "• Consult a doctor if the fever persists or becomes severe."
        ),
        "diabetes": (
            "To manage Diabetes:\n"
            "• Monitor your Blood Sugar levels regularly.\n"
            "• Limit white rice, sweets, and processed foods.\n"
            "• Aim for 30–45 minutes of daily brisk walking.\n"
            "• Take prescribed medicines like Metformin on time after meals."
        ),
        "bp": (
            "To control Blood Pressure:\n"
            "• Reduce sodium and salt intake in meals.\n"
            "• Exercise or brisk walk for 30 minutes daily.\n"
            "• Manage stress with light yoga or meditation.\n"
            "• Take prescribed Blood Pressure medication like Amlodipine regularly."
        ),
        "report": (
            "Your recent lab report summary:\n"
            "• Fasting Blood Sugar: 118 mg/dL (Slightly elevated)\n"
            "• LDL Cholesterol: 142 mg/dL (Borderline high)\n"
            "• HbA1c: 6.2% (Near pre-diabetic range)\n"
            "• Kidney Function and Hemoglobin are normal.\n"
            "• Focus on diet changes, regular walking, and medication adherence."
        ),
        "foods": (
            "Dietary guidance:\n"
            "• Limit white rice, refined carbs, fried foods, and sugary drinks.\n"
            "• Prefer millets, whole grains, leafy greens, and lean protein.\n"
            "• Consume small, frequent, fiber-rich meals."
        ),
        "metformin": (
            "About Metformin:\n"
            "• Metformin is a first-line medication for Type 2 Diabetes.\n"
            "• It helps reduce glucose production in the liver.\n"
            "• Always take it with or after meals to prevent upset stomach.\n"
            "• Contact your doctor if you experience severe nausea."
        ),
        "water": (
            "Hydration tips:\n"
            "• Drink at least 2.5 to 3 litres of water daily.\n"
            "• A glass of warm water in the morning aids digestion."
        ),
        "greeting": (
            "Hello! I am your HealthVerse AI healthcare assistant.\n"
            "• Explain lab reports & tests\n"
            "• Understand medications (Metformin, Amlodipine, etc.)\n"
            "• Provide diet & exercise suggestions\n"
            "How can I assist you today?"
        ),
        "thanks": (
            "You are welcome! Take care of your health.\n"
            "• Feel free to ask any other questions anytime."
        ),
        "default": (
            "I'm your HealthVerse AI assistant. I can assist you with:\n"
            "• Understanding lab reports & vital readings\n"
            "• Guidance on Diabetes, Blood Pressure & fever\n"
            "• Diet plans, exercise routines, and medication info"
        )
    },
    "ta": {
        "fever": (
            "உங்களுக்கு காய்ச்சல் இருந்தால்:\n"
            "• போதுமான அளவு தண்ணீர் குடியுங்கள்.\n"
            "• ஓய்வு எடுங்கள்.\n"
            "• காய்ச்சல் அதிகமாக இருந்தால் மருத்துவரை அணுகவும்.\n"
            "• மூச்சுத் திணறல் அல்லது தீவிர அறிகுறிகள் இருந்தால் உடனடியாக மருத்துவமனைக்குச் செல்லவும்."
        ),
        "diabetes": (
            "Diabetes கட்டுப்பாட்டிற்கு:\n"
            "• உங்கள் Blood Sugar அளவை தவறாமல் பரிசோதிக்கவும்.\n"
            "• வெள்ளை அரிசி, இனிப்புகள் மற்றும் Processed Foods தவிர்க்கவும்.\n"
            "• தினமும் 30-45 நிமிடங்கள் Brisk Walking செய்யவும்.\n"
            "• மருத்துவர் பரிந்துரைத்த Metformin மருந்துகளை சரியான நேரத்தில் எடுத்துக்கொள்ளவும்."
        ),
        "bp": (
            "Blood Pressure பராமரிக்க:\n"
            "• உணவில் உப்பின் (Salt) அளவைக் குறைக்கவும்.\n"
            "• தினமும் 30 நிமிடங்கள் நடைபயிற்சி செய்யவும்.\n"
            "• மன அழுத்தத்தைக் குறைக்க யோகா அல்லது தியானம் செய்யவும்.\n"
            "• Amlodipine போன்ற மருந்துகளை ஒழுங்காக எடுத்துக்கொள்ளவும்."
        ),
        "report": (
            "உங்கள் ஆய்வக அறிக்கையின் விவரம்:\n"
            "• Fasting Blood Sugar: 118 mg/dL (சற்றே அதிகம்)\n"
            "• LDL Cholesterol: 142 mg/dL (எல்லைக்கோடு அதிகம்)\n"
            "• HbA1c: 6.2% (Pre-diabetes அளவிற்கு அருகில்)\n"
            "• Kidney Function மற்றும் Hemoglobin இயல்பாக உள்ளன."
        ),
        "foods": (
            "உணவுப் பழக்கங்கள்:\n"
            "• வெள்ளை அரிசி, இனிப்பு மற்றும் வறுத்த உணவுகளைக் குறைக்கவும்.\n"
            "• கேழ்வரகு, கம்பு, தானியங்கள் மற்றும் காய்கறிகளைச் சேர்க்கவும்."
        ),
        "metformin": (
            "Metformin பற்றிய தகவல்:\n"
            "• Metformin வகை 2 Diabetes சிகிச்சைக்கான மருந்து.\n"
            "• உணவிற்குப் பிறகு எடுத்துக்கொள்ளவும்."
        ),
        "water": (
            "நீர் அருந்துதல்:\n"
            "• தினமும் 2.5 முதல் 3 லிட்டர் தண்ணீர் குடியுங்கள்."
        ),
        "greeting": (
            "வணக்கம்! நான் உங்கள் HealthVerse AI மருத்துவ உதவியாளர்.\n"
            "• ஆய்வக அறிக்கைகள்\n"
            "• மருந்துகள் மற்றும் உணவு முறைகள்\n"
            "உங்களுக்கு எவ்வாறு உதவ வேண்டும்?"
        ),
        "thanks": (
            "நன்றி! உங்கள் ஆரோக்கியத்தைப் பாதுகாத்துக் கொள்ளுங்கள்."
        ),
        "default": (
            "நான் உங்கள் HealthVerse AI உதவியாளர்.\n"
            "• அறிக்கைகளை எளிதாகப் புரிந்துகொள்ள\n"
            "• Diabetes மற்றும் இரத்த அழுத்தம் பற்றிய வழிகாட்டுதலுக்கு"
        )
    },
    "te": {
        "fever": (
            "మీకు జ్వరం ఉంటే:\n"
            "• తగినంత నీరు తాగండి.\n"
            "• విశ్రాంతి తీసుకోండి.\n"
            "• జ్వరం ఎక్కువగా ఉంటే వైద్యుడిని సంప్రదించండి.\n"
            "• శ్వాస తీసుకోవడంలో ఇబ్బంది లేదా తీవ్రమైన లక్షణాలు ఉంటే వెంటనే ఆసుపత్రికి వెళ్లండి."
        ),
        "diabetes": (
            "Diabetes నియంత్రణకు:\n"
            "• మీ Blood Sugar స్థాయిలను క్రమం తప్పకుండా పరీక్షించండి.\n"
            "• తెల్ల బియ్యం, మిఠాయిలు మరియు Processed Foods పరిమితం చేయండి.\n"
            "• రోజూ 30-45 నిమిషాల పాటు Brisk Walking చేయండి.\n"
            "• వైద్యులు సూచించిన Metformin మరియు ఇతర మందులను సమయానికి తీసుకోండి."
        ),
        "bp": (
            "Blood Pressure నియంత్రణకు:\n"
            "• ఆహారంలో ఉప్పు (Salt) శాతం తగ్గించండి.\n"
            "• రోజుకి 30 నిమిషాల పాటు వ్యాయామం చేయండి.\n"
            "• Amlodipine మందులను వేళకు తీసుకోండి."
        ),
        "report": (
            "మీ ల్యాబ్ రిపోర్ట్ సారాంశం:\n"
            "• Fasting Blood Sugar: 118 mg/dL (కొంచెం ఎక్కువ)\n"
            "• LDL Cholesterol: 142 mg/dL (సరిహద్దు ఎక్కువ)\n"
            "• HbA1c: 6.2% (Pre-diabetes స్థాయి వద్ద)\n"
            "• కిడ్నీ పనితీరు మరియు Hemoglobin సాధారణంగా ఉన్నాయి."
        ),
        "foods": (
            "ఆహార సూచనలు:\n"
            "• తెల్ల బియ్యం, తీపి పదార్థాలు తగ్గించండి.\n"
            "• జొన్నలు, రాగులు, కూరగాయలు ఎక్కువగా తీసుకోండి."
        ),
        "metformin": (
            "Metformin సమాచారం:\n"
            "• Metformin టైప్ 2 Diabetes నియంత్రణకు వాడతారు.\n"
            "• భోజనం తర్వాత వేసుకోవాలి."
        ),
        "water": (
            "మంచినీరు తీసుకోవడం:\n"
            "• రోజుకి 2.5 నుండి 3 లీటర్ల నీరు తాగండి."
        ),
        "greeting": (
            "నమస్కారం! నేను మీ HealthVerse AI వైద్య సహాయకుడిని.\n"
            "• మీ రిపోర్టుల వివరణ\n"
            "• మందులు మరియు ఆహార సూచనలు\n"
            "నేను మీకు ఎలా సహాయపడగలను?"
        ),
        "thanks": (
            "ధన్యవాదాలు! మీ ఆరోగ్యాన్ని జాగ్రత్తగా చూసుకోండి."
        ),
        "default": (
            "నేను మీ HealthVerse AI సహాయకుడిని.\n"
            "• రిపోర్టులు అర్థం చేసుకోవడానికి\n"
            "• Diabetes, BP ఇతర ఆరోగ్య సందేహాలకు నివృత్తి"
        )
    },
    "ml": {
        "fever": (
            "നിങ്ങൾക്ക് പനിയുണ്ടെങ്കിൽ:\n"
            "• ആവശ്യത്തിന് വെള്ളം കുടിക്കുക.\n"
            "• വിശ്രമിക്കുക.\n"
            "• പനി കൂടുതലാണെങ്കിൽ ഡോക്ടറെ കാണുക.\n"
            "• ശ്വാസമെടുക്കാൻ ബുദ്ധിമുട്ടോ ഗുരുതരമായ ലക്ഷണങ്ങളോ ഉണ്ടെങ്കിൽ ഉടൻ ആശുപത്രിയിൽ പോകുക."
        ),
        "diabetes": (
            "Diabetes നിയന്ത്രണത്തിനായി:\n"
            "• നിങ്ങളുടെ Blood Sugar അളവ് പതിവായി പരിശോധിക്കുക.\n"
            "• വെള്ള അരി, മധുരം, Processed Foods എന്നിവ കുറയ്ക്കുക.\n"
            "• ദിവസവും 30-45 മിനിറ്റ് Brisk Walking ചെയ്യുക.\n"
            "• ഡോക്ടർ നിർദ്ദേശിച്ച Metformin മരുന്നുകൾ കൃത്യസമയത്ത് കഴിക്കുക."
        ),
        "bp": (
            "Blood Pressure നിയന്ത്രിക്കാൻ:\n"
            "• ഭക്ഷണത്തിൽ ഉപ്പിന്റെ (Salt) അളവ് കുറയ്ക്കുക.\n"
            "• ദിവസവും 30 മിനിറ്റ് വ്യായാമം ചെയ്യുക.\n"
            "• Amlodipine മരുന്നുകൾ സമയത്തിന് കഴിക്കുക."
        ),
        "report": (
            "നിങ്ങളുടെ ലാബ് റിപ്പോർട്ട് വിവരം:\n"
            "• Fasting Blood Sugar: 118 mg/dL (ചെറുതായി ഉയർന്നത്)\n"
            "• LDL Cholesterol: 142 mg/dL (അതിർത്തി ഉയർന്നത്)\n"
            "• HbA1c: 6.2% (Pre-diabetes ലെവലിനോട് അടുത്ത്)\n"
            "• Kidney Function, Hemoglobin എന്നിവ സാധാരണ നിലയിലാണ്."
        ),
        "foods": (
            "ഭക്ഷണ ശീലങ്ങൾ:\n"
            "• വെള്ള അരി, മധുരം, വറുത്ത സാധനങ്ങൾ എന്നിവ ഒഴിവാക്കുക.\n"
            "• ചെറുധാന്യങ്ങൾ, പച്ചക്കറികൾ എന്നിവ ഭക്ഷണത്തിൽ ഉൾപ്പെടുത്തുക."
        ),
        "metformin": (
            "Metformin മരുന്നിനെക്കുറിച്ച്:\n"
            "• Type 2 Diabetes നിയന്ത്രണത്തിനാണ് Metformin നൽകുന്നത്.\n"
            "• ഭക്ഷണത്തിന് ശേഷം കഴിക്കുക."
        ),
        "water": (
            "വെള്ളം കുടിക്കുന്നതിനെക്കുറിച്ച്:\n"
            "• പ്രതിദിനം 2.5 - 3 ലിറ്റർ വെള്ളം കുടിക്കുക."
        ),
        "greeting": (
            "ഹലോ! ഞാൻ നിങ്ങളുടെ HealthVerse AI മെഡിക്കൽ സഹായിയാണ്.\n"
            "• ലാബ് റിപ്പോർട്ടുകൾ മനസ്സിലാക്കാൻ\n"
            "• മരുന്നുകൾ, ആഹാരം എന്നിവയെക്കുറിച്ചുള്ള സംശയങ്ങൾക്ക്\n"
            "ഞാൻ എങ്ങനെ സഹായിക്കേണ്ടത്?"
        ),
        "thanks": (
            "നന്ദി! ആരോഗ്യം ശ്രദ്ധിക്കുക."
        ),
        "default": (
            "ഞാൻ നിങ്ങളുടെ HealthVerse AI സഹായിയാണ്.\n"
            "• ലാബ് റിപ്പോർട്ടുകൾ വിശകലനം ചെയ്യാൻ\n"
            "• Diabetes, Blood Pressure സംശയങ്ങൾക്ക് പരിഹാരം"
        )
    },
    "mr": {
        "fever": (
            "तुम्हाला ताप असल्यास:\n"
            "• पुरेसे पाणी प्या.\n"
            "• विश्रांती घ्या.\n"
            "• जास्त ताप असल्यास डॉक्टरांचा सल्ला घ्या.\n"
            "• श्वास घेण्यास त्रास किंवा गंभीर लक्षणे असल्यास त्वरित रुग्णालयात जा."
        ),
        "diabetes": (
            "Diabetes नियंत्रित ठेवण्यासाठी:\n"
            "• तुमची Blood Sugar पातळी नियमित तपासा.\n"
            "• पांढरा भात, गोड पदार्थ आणि Processed Foods टाळा.\n"
            "• रोज 30-45 मिनिटे Brisk Walking करा.\n"
            "• डॉक्टरांनी दिलेली Metformin आणि औषधे वेळेवर घ्या."
        ),
        "bp": (
            "Blood Pressure नियंत्रणात ठेवण्यासाठी:\n"
            "• जेवणातील मिठाचे (Salt) प्रमाण कमी करा.\n"
            "• दररोज 30 मिनिटे हलका व्यायाम करा.\n"
            "• Amlodipine सारखी औषधे वेळेवर घ्या."
        ),
        "report": (
            "तुमच्या लॅब रिपोर्टचा तपशील:\n"
            "• Fasting Blood Sugar: 118 mg/dL (थोडी जास्त)\n"
            "• LDL Cholesterol: 142 mg/dL (सीमा ओलांडली)\n"
            "• HbA1c: 6.2% (Pre-diabetes पातळी जवळ)\n"
            "• Kidney Function आणि Hemoglobin सामान्य आहेत."
        ),
        "foods": (
            "आहारविषयक सूचना:\n"
            "• पांढरा भात आणि तळलेले पदार्थ कमी करा.\n"
            "• ज्वारी, बाजरी, नाचणी आणि हिरव्या भाज्या खा."
        ),
        "metformin": (
            "Metformin बद्दल माहिती:\n"
            "• Metformin ही Type 2 Diabetes साठी दिली जाणारी औषध आहे.\n"
            "• जेवणानंतर औषध घ्या."
        ),
        "water": (
            "पाणी पिण्याबाबत:\n"
            "• रोज 2.5 ते 3 लिटर पाणी प्या."
        ),
        "greeting": (
            "नमस्कार! मी आपला HealthVerse AI वैद्यकीय सहाय्यक आहे.\n"
            "• लॅब रिपोर्ट्स स्पष्टीकरण\n"
            "• औषधे आणि आहाराचा सल्ला\n"
            "मी तुम्हाला कशी मदत करू शकतो?"
        ),
        "thanks": (
            "धन्यवाद! आपल्या आरोग्याची काळजी घ्या."
        ),
        "default": (
            "मी आपला HealthVerse AI सहाय्यक आहे.\n"
            "• रिपोर्ट्स समजून घेण्यासाठी\n"
            "• Diabetes आणि Blood Pressure संदर्भातील माहितीसाठी"
        )
    },
    "tcy": {
        "fever": (
            "ಇರೆಗ್ ಜ್ವರ ಉಂಡುಂದ್ ಆಂಡ:\n"
            "• ಬೋಡಾಯಿನಾತ್ ನೀರ್ ಪರ್ಲೆ.\n"
            "• ವಿಶ್ರಾಂತಿ ದೆತೊನುಲೆ.\n"
            "• ಜ್ವರ ಜಾಸ್ತಿ ಇತ್ತ್‌ಂಡ ಡಾಕ್ಟರೆನ್ ಭೇಟಿ ಮಾಡಿ.\n"
            "• ಉಸಿರಾಟದ ತೊಂದರೆ ಅಥವಾ ಗಂಭೀರ ಲಕ್ಷಣ ಇತ್ತ್‌ಂಡ ತಕ್ಷಣ ಹಾಸ್ಪೆಟಲ್‌ಗ್ ಪೋಲೆ."
        ),
        "diabetes": (
            "Diabetes ನಿಯಂತ್ರಣ ಮಲ್ಪೆರೆ:\n"
            "• Blood Sugar ಲೆವೆಲ್‌ನ್ ಡೈಲಿ ಚೆಕ್ ಮಲ್ಪೆ.\n"
            "• ಬೊಳ್ಳಿ ಅರಿ, ಸಿಹಿ ಬೊಕ್ಕ ತೈಲೊದ ತಿನಸ್ ಕಮ್ಮಿ ಮಲ್ಪೆ.\n"
            "• ಪ್ರತಿದಿನ 30-45 ನಿಮಿಷ Brisk Walking ಮಲ್ಪೆ.\n"
            "• ಡಾಕ್ಟರ್ ಪಂಡಿನ Metformin ಮರ್ದ್ ಸಮಯೊಗು ದೆತೊನುಲೆ."
        ),
        "bp": (
            "Blood Pressure ಕಂಟ್ರೋಲ್‌ಡ್ ದೀಪೆರೆ:\n"
            "• ವನಸ್‌ಡ್ ಉಪ್ಪುದ ಪ್ರಮಾಣ ಕಮ್ಮಿ ಮಲ್ಪೆ.\n"
            "• ಡೈಲಿ 30 ನಿಮಿಷ ನಡಪುಲೆ ಅತ್ತ್‌ಂಡ ವ್ಯಾಯಾಮ ಮಲ್ಪೆ.\n"
            "• Amlodipine ಮರ್ದ್ ಸಮಯೊಗು ದೆತೊನುಲೆ."
        ),
        "report": (
            "ಇರೆನ ಲ್ಯಾಬ್ ರಿಪೋರ್ಟ್‌ದ ವಿವರೊ:\n"
            "• Fasting Blood Sugar: 118 mg/dL (ಸ್ವಲ್ಪ ಜಾಸ್ತಿ)\n"
            "• LDL Cholesterol: 142 mg/dL (ಸೀಮಾರೇಖೆ ಜಾಸ್ತಿ)\n"
            "• HbA1c: 6.2% (Pre-diabetes ಗೆ ಕೈತಲ್)\n"
            "• Kidney Function ಬೊಕ್ಕ Hemoglobin ಸಾಮಾನ್ಯ ಉಂಡು."
        ),
        "foods": (
            "ಆಹಾರೊದ ಸಲಹೆಲು:\n"
            "• ಬೊಳ್ಳಿ ಅರಿ ಬೊಕ್ಕ ಎಣ್ಣೆಡ್ ಪುರಿದಿನ ತಿನಸ್ ಕಮ್ಮಿ ಮಲ್ಪೆ.\n"
            "• ರಾಗಿ, ಜೋಳ ಬೊಕ್ಕ ತರಕಾರಿ ಜಾಸ್ತಿ ತಿನೊಲಿ."
        ),
        "metformin": (
            "Metformin ದ ಮಾಹಿತಿ:\n"
            "• Metformin ಪನ್ಪಿನ ಮರ್ದ್ Type 2 Diabetes ಕಂಟ್ರೋಲ್‌ಗ್ ಕೋರ್ಪಿನಿ.\n"
            "• ತಿನಸ್ ಮಲ್ತಿನ ಬುಕ್ಕೊ ದೆತೊನುಲೆ."
        ),
        "water": (
            "ನೀರ್ ಪರ್ಪಿನ ಬಗ್ಗೆ:\n"
            "• ದಿನೊಕ್ಕು 2.5 ತರ್ದ್ 3 ಲೀಟರ್ ನೀರ್ ಪರ್ಲೆ."
        ),
        "greeting": (
            "ನಮಸ್ಕಾರ! ಯಾನ್ ಇರೆನ HealthVerse AI ಸಹಾಯಕ.\n"
            "• ಲ್ಯಾಬ್ ರಿಪೋರ್ಟ್‌ದ ಅರ್ಥ ತೆರಿಯೆರೆ\n"
            "• ಮರ್ದ್ ಬೊಕ್ಕ ಆಹಾರೊದ ಮಾಹಿತಿ ಪಡೆಯೆರೆ\n"
            "ಯಾನ್ ಇರೆಗ್ ಎಂಚ ಸಾಯ ಮಲ್ಪೊಲಿ?"
        ),
        "thanks": (
            "ಸೊಲ್ಮೆಲು! ಇರೆನ ಆರೋಗ್ಯ ಎಡ್ಡೆ ದೀಲೆ."
        ),
        "default": (
            "ಯಾನ್ ಇರೆನ HealthVerse AI ಸಹಾಯಕೆ.\n"
            "• ರಿಪೋರ್ಟ್‌ದ ವಿವರೊ ತಿಳಿಯೆರೆ\n"
            "• Diabetes ಬೊಕ್ಕ BP ದ ಸಲಹೆ ಪಡೆಯೆರೆ"
        )
    }
}


def analyze_report(filename: str, raw_text: str = "") -> dict:
    """Simulate OCR + medical AI analysis."""
    analysis = dict(SAMPLE_ANALYSIS)
    analysis["filename"] = filename
    analysis["analyzed_at"] = datetime.utcnow().isoformat() + "Z"
    analysis["ocr_confidence"] = round(random.uniform(0.88, 0.98), 2)
    text_lower = (raw_text or "").lower()
    analysis["ocr_detected"] = "glucose" in text_lower or "sugar" in text_lower or bool(raw_text)
    return analysis


def translate_analysis(analysis: dict, lang: str) -> dict:
    """Return translated summary + findings for supported languages."""
    if lang == "en" or lang not in TRANSLATIONS:
        return {
            "lang": "en",
            "summary": analysis.get("summary", ""),
            "findings": [
                f"{f['parameter']}: {f['value']} ({f['note'] or f['status']})"
                for f in analysis.get("findings", [])
            ]
        }
    t = TRANSLATIONS[lang]
    return {
        "lang": lang,
        "summary": t["summary"],
        "findings": t["findings"]
    }


def chat_reply(message: str, history: list = None, lang: str = "en") -> str:
    """
    Multilingual AI Health Assistant Response Generator.
    Strictly enforces:
    1. Language detection on user's latest message.
    2. Responding ONLY in the user's detected language.
    3. Keeping standard medical terms in English.
    4. Using bullet points and clean structure.
    """
    msg = (message or "").strip()
    if not msg:
        return "Please ask a question about your health or report."

    # 1. Detect language of user's message
    user_lang = detect_language(msg, default_lang=lang)

    # Check if English translation requested
    if re.search(r'\b(in english|translate to english|english response)\b', msg.lower()):
        user_lang = "en"

    # Get response dict for user language
    resp_dict = RESPONSES_BY_LANG.get(user_lang, RESPONSES_BY_LANG["en"])
    msg_lower = msg.lower()

    # 2. Topic matching
    # Fever (Kannada: ಜ್ವರ, Hindi: बुखार, Tamil: காய்ச்சல், Telugu: జ్వరం, Malayalam: പനി, Marathi: ताप, Tulu: ಜ್ವರ)
    if re.search(r'(fever|feverish|ಜ್ವರ|ಬುಖಾರ್|बुखार|காய்ச்சல்|జ్వరం|പനി|ताप|jwara|jwaram|bukhar|pani|kaichal)', msg_lower):
        return resp_dict["fever"]

    # Diabetes / Blood Sugar / Glucose
    if re.search(r'(diabetes|sugar|glucose|hba1c|ಪ್ರಮೇಹ|मधुमेह|நீரிழிவு|మధుమేహం|പ്രമേഹം|डायबिटीज|ಡಯಾಬಿಟಿಸ್)', msg_lower):
        return resp_dict["diabetes"]

    # Blood Pressure / Hypertension
    if re.search(r'(bp|blood pressure|hypertension|ರಕ್ತದೊತ್ತಡ|रक्तचाप|இரத்த அழுத்தம்|రక్తపోటు|രക്തസമ്മർദ്ദം|रक्तदाब)', msg_lower):
        return resp_dict["bp"]

    # Lab Reports / Analysis
    if re.search(r'(report|lab|blood|result|analysis|findings|ವರದಿ|रिपोर्ट|அறிக்கை|రిపోర్ట్|റിപ്പോർട്ട്|ರಿಪೋರ್ಟ್)', msg_lower):
        return resp_dict["report"]

    # Foods / Diet / Rice
    if re.search(r'(food|eat|diet|avoid|rice|ಆಹಾರ|ಅಕ್ಕಿ|खाना|भोजन|चावल|உணவு|அரிசி|ఆహారం|బియ్యం|ഭക്ഷണം|അരി|आहार|भात|ತಿನಸ್|ಅರಿ)', msg_lower):
        return resp_dict["foods"]

    # Metformin / Medicines
    if re.search(r'(metformin|medicine|drug|tablet|pill|ಔಷಧಿ|ಮರ್ದ್|दवा|மருந்து|మందులు|മരുന്ന്|औषध)', msg_lower):
        return resp_dict["metformin"]

    # Water / Hydration
    if re.search(r'(water|hydrat|ನೀರು|पानी|தண்ணீர்|నీళ్ళు|വെള്ളം|पाणी|ನೀರ್)', msg_lower):
        return resp_dict["water"]

    # Greetings
    if re.search(r'(hello|hi |hey|namaste|namaskara|namaskar|vanakkam|namaskaram|ನಮಸ್ಕಾರ|नमस्ते|வணக்கம்|నమస్కారం|ഹലോ)', msg_lower):
        return resp_dict["greeting"]

    # Thanks
    if re.search(r'(thank|thanks|dhanyavad|solmelu|ಧನ್ಯವಾದ|धन्यवाद|நன்றி|ధన్యవాదాలు|നന്ദി|ಸೊಲ್ಮೆಲು)', msg_lower):
        return resp_dict["thanks"]

    return resp_dict["default"]


def generate_health_score(profile: dict, metrics: dict) -> int:
    """Simple heuristic health score 40–95."""
    score = 78
    if profile:
        age = profile.get("age") or 40
        if age > 60:
            score -= 5
        diseases = (profile.get("diseases") or "").lower()
        if "diabetes" in diseases:
            score -= 8
        if "hypertension" in diseases or "bp" in diseases:
            score -= 5
    if metrics:
        adherence = metrics.get("medicine_adherence") or 0
        if adherence > 80:
            score += 5
        water = metrics.get("water_liters") or 0
        target = metrics.get("water_target") or 2.5
        if water >= target * 0.8:
            score += 3
    return max(40, min(95, score))
