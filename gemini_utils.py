import os
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime, timedelta
import google.generativeai as genai

# Load .env and configure API
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini 2.5 Flash for faster, cheaper output
MODEL_NAME = "models/gemini-2.5-flash"
memory_store = defaultdict(list)  # {user_id: [(timestamp, message)]}

SYSTEM_PROMPT = """
🔮 TACX Ayurvedic AI Support (WhatsApp Version)

You are TACX – the Ayurvedic AI Expert of The Ayurveda Co.
ONLY answer health, beauty & wellness queries rooted in Ayurveda × Modern Science.
Do NOT reply to greetings, order tracking, refund, complaint, or delivery-related topics.

🧠 Smart Quiz Logic:
- Trigger 3-step quiz for body-related problems (hair fall, gas, sleep)
- Never repeat quiz unless user re-mentions symptom
- Wait for quiz response before suggesting product again

🌿 Use Hinglish, reply in max 6 lines, and add emojis + product suggestion at end.

⭐ Recommended TACX Product:
🧴 *Product Name*
🔘 [🛒 Buy Now] [📖 Learn More]
"""

def add_to_memory(user_id, user_text):
    memory_store[user_id].append((datetime.utcnow(), user_text))

def get_recent_history(user_id):
    now = datetime.utcnow()
    # Keep only messages from last 10 minutes
    recent = [
        (ts, msg) for ts, msg in memory_store[user_id]
        if now - ts < timedelta(minutes=10)
    ]
    memory_store[user_id] = recent
    return recent[-5:]  # Limit to last 5

def get_gemini_reply(user_id, user_text):
    add_to_memory(user_id, user_text)
    try:
        history = get_recent_history(user_id)
        messages = [{"role": "user", "parts": [SYSTEM_PROMPT]}]
        for _, msg in history:
            messages.append({"role": "user", "parts": [msg]})
        messages.append({"role": "user", "parts": [user_text]})

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(messages)
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini Error:", e)
        if "quota" in str(e).lower():
            return "⚠️ AI quota limit reached. Please try again later. We're working to restore the service. 🙏"
        return "❌ Gemini Fallback Error: Unable to respond at the moment. Please rephrase or try later."
