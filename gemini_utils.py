import os
from dotenv import load_dotenv
import google.generativeai as genai
from collections import defaultdict
from datetime import datetime, timedelta

# Load .env and configure API
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini model & memory
MODEL_NAME = "models/gemini-1.5-pro-latest"
memory_store = defaultdict(list)  # user_id → [(timestamp, message)]

# System Prompt
SYSTEM_PROMPT = """
🔮 TACX Ayurvedic AI Support (WhatsApp Version)

You are TACX – the Ayurvedic AI Expert of The Ayurveda Co.
ONLY answer health, beauty & wellness queries rooted in Ayurveda × Modern Science.
Never reply to greetings, coupon/refund/order/delivery or unrelated topics.

Reply in Hinglish, use crisp 5-6 line messages with emojis and varied tones.

Handle health/body queries with smart quizzes in 3 steps.
Do NOT re-trigger quizzes if user ignores them.
ALWAYS end response with:

⭐ Recommended TACX Product:  
🧴 *Product Name*  
🔘 [🛒 Buy Now] [📖 Learn More]
"""

def get_recent_history(user_id):
    now = datetime.utcnow()
    memory_store[user_id] = [
        (ts, msg) for ts, msg in memory_store[user_id]
        if now - ts < timedelta(minutes=10)
    ]
    return memory_store[user_id][-5:]

def add_to_memory(user_id, msg):
    memory_store[user_id].append((datetime.utcnow(), msg))

def get_gemini_reply(user_id, user_text):
    add_to_memory(user_id, user_text)
    try:
        history = get_recent_history(user_id)
        conversation = [{"role": "user", "parts": [SYSTEM_PROMPT]}]
        for _, msg in history:
            conversation.append({"role": "user", "parts": [msg]})
        conversation.append({"role": "user", "parts": [user_text]})

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(conversation)
        return response.text.strip()

    except Exception as e:
        print("❌ Gemini Error:", e)
        if "429" in str(e):
            return (
                "⚠️ AI quota limit reached. Please try again later. "
                "We're working to restore the service. 🙏"
            )
        return (
            "🧠 Sorry! AI system is overloaded right now. "
            "But here's a general remedy for common issues:\n\n"
            "💊 Ashwagandha Capsules + Tulsi Tea\n\n"
            "⭐ Recommended TACX Product:\n"
            "🧴 Daily Balance Pack\n🔘 [🛒 Buy Now] [📖 Learn More]"
        )

  