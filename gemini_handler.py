import os
import google.generativeai as genai

GEMINI_KEYWORDS = {
    "kumkumadi": [
        "kumkumadi", "kumkumadi oil", "kumkumadi tailam",
        "kumkumadi serum", "kumkumadi benefits", "face oil"
    ],
    "ubtan": [
        "ubtan", "ubtan scrub", "natural face scrub"
    ],
    "pcos": [
        "pcos", "pcod", "irregular periods", "hormonal balance"
    ],
    "triphala": [
        "triphala", "triphala churna", "constipation", "digestion"
    ],
    "ashwagandha": [
        "ashwagandha", "ashwagandha tablets", "stress", "sleep"
    ],
    "haircare": [
        "hair oil", "hair fall", "dry scalp"
    ],
    "skincare": [
        "face serum", "face wash", "acne", "glow skin"
    ],
    "digestion": [
        "digestion", "acidity", "bloating", "gut health"
    ],
    "immunity": [
        "boost immunity", "cold and cough", "fever", "kadha"
    ],
    "bodycare": [
        "body wash", "body lotion", "dry skin"
    ]
}

def smart_gemini_reply(user_message):
    for topic, keywords in GEMINI_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in user_message.lower():
                return generate_gemini_answer(user_message)
    return None

def generate_gemini_answer(prompt):
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini error:", e)
        return None
