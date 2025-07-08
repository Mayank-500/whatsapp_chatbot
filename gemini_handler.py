import os
import google.generativeai as genai

# Keywords mapped to company-related topics
GEMINI_KEYWORDS = {
    "kumkumadi": [
        "kumkumadi", "kumkumadi oil", "kumkumadi tailam",
        "kumkumadi face oil", "kumkumadi serum", "kumkumadi benefits",
        "kumkumadi uses", "face oil for glowing skin"
    ],
    "ubtan": [
        "ubtan", "ubtan face pack", "ubtan scrub", "natural face scrub", "herbal ubtan"
    ],
    "pcos": [
        "pcos", "pcod", "irregular periods", "hormonal balance",
        "fertility support", "ayurvedic medicine for pcos"
    ],
    "triphala": [
        "triphala", "triphala churna", "triphala powder",
        "constipation remedy", "digestion remedy", "triphala benefits"
    ],
    "ashwagandha": [
        "ashwagandha", "ashwagandha tablets", "stress relief",
        "energy booster", "sleep improvement", "ayurvedic immunity booster"
    ],
    "haircare": [
        "hair oil", "hair fall", "dry scalp",
        "ayurvedic hair treatment", "natural hair oil", "hair serum"
    ],
    "skincare": [
        "face serum", "face wash", "glow skin", "acne",
        "pigmentation", "natural skincare", "herbal skincare"
    ],
    "digestion": [
        "digestion", "acidity", "bloating", "gut health",
        "digestive syrup", "indigestion"
    ],
    "immunity": [
        "boost immunity", "cold and cough", "fever",
        "natural kadha", "immune booster syrup", "ayurvedic immunity booster"
    ],
    "bodycare": [
        "body wash", "body lotion", "dry skin", "moisturizer", "natural body lotion"
    ]
}

def smart_gemini_reply(user_message):
    user_msg = user_message.lower()
    for topic, keywords in GEMINI_KEYWORDS.items():
        for keyword in keywords:
            if keyword in user_msg or user_msg in keyword or any(k in user_msg.split() for k in keyword.split()):
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
