import os
import string
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key

ABUSIVE_KEYWORDS = [
    # English
    "fuck", "fucking", "fucker", "motherfucker", "asshole", "dick", "dickhead", "cock", "bastard", "slut", "bitch",
    "jerk", "loser", "cunt", "pussy", "crap", "shit", "bullshit", "suck", "sucker", "screw you", "dumb", "dumbass",
    "retard", "bloody", "bloody fool", "whore", "die bitch", "go to hell", "shut up bitch", "your mom", "hoe",
    "balls", "nuts", "fatass", "lazy fuck", "moron", "stfu", "gtfo", "wanker",

    # Hindi - Romanized
    "bhenchod", "behenchod", "madarchod", "madar chod", "chod", "chodu", "chut", "chutiya", "chutiye", "chuteya",
    "lund", "lavda", "lawda", "randi", "randiya", "gandu", "gaand", "gand", "gand mara", "bsdk", "bhosdike",
    "bhosadi", "bhosda", "bhosri", "bhosrdi", "bhosdika", "ma ki chut", "behen ki chut", "maa chuda", "behen chuda",
    "jhant", "jhantu", "jhant chatu", "jhant ka baal", "jhant ke baal", "chus le", "chusu", "gand chatu",
    "gand mein le", "gand me le", "gaand le", "gaand de", "bhadwa", "bhadwe", "kutta", "kuttiya", "kutti",
    "kamina", "kaminey", "kameena", "suar", "suvar", "hijra", "hizra", "chakka", "gasti", "rakhail", "launda",
    "laundiya", "saala", "sale", "bkl", "mc", "bc", "mc bc", "mcbc", "bcmc", "mcbk", "teri maa", "teri behen",
    "maa ka", "behen ka", "madarchod ke", "bhosdika", "chodunga", "chud gaya", "chod diya", "chod rha hu",
    "bhabhi choda", "sex kar", "chod rha", "gaand mara", "bhosdike", "bhosdiwale", "phuddi", "phuddu", "phuddi chatu",
    "fuddu", "fattu", "laundo", "maal", "doodh", "nipple", "gaand", "gand fat", "chod ke aaya", "jhant chato",
    "chuchu", "chuchi", "boobs", "nangi", "nangi photo", "randi khana", "mms leak", "sex video", "fuck buddy",

    # Hindi abusive phrases (spaced)
    "maa ki chut", "behen ki chut", "maa ka bhosda", "behen ka lund", "maa chuda", "behen chuda", "gand mein le le",
    "chod do", "chod ke aaya", "behen ke lund", "maa ke lund", "mc bc wale", "teri maa ka", "teri maa chud gayi",
    "bhosdi ke", "madarchod saala", "suar ke bachhe", "jhant ke baal", "madarchod", "behenchod", "chod le",
]



FAREWELL_WORDS = ["bye", "goodbye", "take care", "thank you", "thanks", "see you"]

def contains_abuse(text):
    return any(word in text.lower() for word in ABUSIVE_KEYWORDS)

def smart_gemini_reply(user_message):
    if contains_abuse(user_message):
        return "⚠️ Let's keep this respectful. I'm here to help with Ayurveda and wellness only. 🙏"

    try:
        model = "gemini-2.5-pro"
        client = genai.Client()

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)],
            )
        ]

        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text="""
You are an Ayurvedic expert at The Ayurveda Co. (TACX), trained to answer only queries related to Ayurveda x Science.
⛔ Do NOT reply to questions containing words like: ["hi", "hello", "namaste", "shop", "discount", "refund", "policy", "track", "order", "status", "buy"]

✅ Instead:
* Keep answers under 7 lines.
* Always include a relevant Ayurvedic product (name + benefit).
* Offer Discovery Quiz with: Start Quiz, Skip buttons.
* Avoid duplicate "Namaste" or excessive "Start Quiz".

Respond like a warm, intelligent Ayurvedic guide 🌿
""")
            ],
        )

        response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        ):
            response += chunk.text

        response = response.strip()

        # 🧹 Clean "Namaste" repetition
        if response.lower().startswith("namaste"):
            response = response[7:].lstrip(",. ")

        # 👋 Skip quiz on farewell
        if any(word in user_message.lower() for word in FAREWELL_WORDS):
            return response

        # ✅ Append Quiz Suggestion only once
        if "start quiz" not in response.lower():
            response += "\n\n[Start Quiz] [Skip]"

        return response

    except Exception as e:
        print("❌ Gemini error:", e)
        return "⚠️ Sorry, I couldn’t understand that. Please ask about Ayurvedic wellness, herbs, or skincare."
