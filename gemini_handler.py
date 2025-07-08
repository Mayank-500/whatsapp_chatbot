import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-pro")

GEMINI_KEYWORDS = {
    "kumkumadi": [
        "kumkumadi", "kumkumadi oil", "kumkumadi tailam", "kumkumadi face oil",
        "kumkumadi serum", "kumkumadi benefits", "kumkumadi uses", "face oil for glowing skin"
    ],
    "ubtan": [
        "ubtan", "ubtan face pack", "ubtan scrub", "natural face scrub", "herbal ubtan"
    ],
    "pcos": [
        "pcos", "pcod", "irregular periods", "hormonal balance", "fertility support",
        "ayurvedic medicine for pcos"
    ],
    "triphala": [
        "triphala", "triphala churna", "triphala powder", "constipation remedy",
        "digestion remedy", "triphala benefits"
    ],
    "ashwagandha": [
        "ashwagandha", "ashwagandha tablets", "stress relief", "energy booster",
        "sleep improvement", "ayurvedic immunity booster"
    ],
    "haircare": [
        "hair oil", "hair fall", "dry scalp", "ayurvedic hair treatment",
        "natural hair oil", "hair serum"
    ],
    "skincare": [
        "face serum", "face wash", "glow skin", "acne", "pigmentation",
        "natural skincare", "herbal skincare"
    ],
    "digestion": [
        "digestion", "acidity", "bloating", "gut health", "digestive syrup", "indigestion"
    ],
    "immunity": [
        "boost immunity", "cold and cough", "fever", "natural kadha",
        "immune booster syrup", "ayurvedic immunity booster"
    ],
    "bodycare": [
        "body wash", "body lotion", "dry skin", "moisturizer", "natural body lotion"
    ]
}

ALL_KEYWORDS = set(kw.lower() for group in GEMINI_KEYWORDS.values() for kw in group)

def is_gemini_relevant(message: str) -> bool:
    message = message.lower()
    return any(keyword in message for keyword in ALL_KEYWORDS)

def ask_gemini(message: str) -> str | None:
    if not is_gemini_relevant(message):
        return None
    try:
        response = model.generate_content(message)
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini error:", e)
        return None
