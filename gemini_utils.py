import os
from dotenv import load_dotenv
import google.generativeai as genai
from collections import defaultdict
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# ✅ Use the faster, quota-efficient model
MODEL_NAME = "models/gemini-2.5-flash"
memory_store = defaultdict(list)  # user_id → list of (timestamp, message)

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
    history = memory_store[user_id]
    now = datetime.utcnow()
    # keep only last 5 messages from past 10 mins
    memory_store[user_id] = [
        (ts, msg) for ts, msg in history if now - ts < timedelta(minutes=10)
    ]
    return memory_store[user_id][-5:]

def add_to_memory(user_id, user_text):
    memory_store[user_id].append((datetime.utcnow(), user_text))

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
        return "⚠️ Gemini AI quota limit reached or failed to respond. Please try again later."

