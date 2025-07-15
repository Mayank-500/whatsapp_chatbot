# pip install google-generativeai
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env
load_dotenv()

# API Key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Models
PRIMARY_MODEL = "models/gemini-2.5-flash"
FALLBACK_MODEL = "models/gemini-pro"

# System prompt
SYSTEM_PROMPT = """
🔮 TACX Ayurvedic AI Support (WhatsApp Version)

You are TACX – the Ayurvedic AI Expert of The Ayurveda Co.  
Respond ONLY to health, beauty & wellness topics rooted in Ayurveda × Modern Science.  
Focus Areas: Doshas, skin/hair/body issues, sleep, gut, mental health, herbs, beauty, energy, immunity, etc.

🚫 Strictly DO NOT reply to:
hi, hello, namaste, hey, morning, coupon, refund, complaint, abuse, delivery, order, track status — or any non-ayurvedic conversation.

✅ Conversational Rules:
- Keep reply short, crisp, max 6 lines
- Use Hinglish (Hindi+English), like a friendly Ayurvedic doctor
- Use creative, varied response styles (✨ emojis, ⭐ bullets, 🔗 CTA buttons)
- Maintain memory for flowing conversations
- Never sound robotic or repetitive

🧠 Smart Quiz System (Only for Body-Related Concerns):
... (truncated for brevity, include your full prompt here if needed)
"""

def generate_with_model(model_name, user_query):
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(
        contents=[
            {"role": "user", "parts": [SYSTEM_PROMPT + f"\n\nUser: {user_query}"]}
        ]
    )
    return response.text.strip()

def get_gemini_reply(user_query):
    try:
        return generate_with_model(PRIMARY_MODEL, user_query)
    except Exception as e:
        print(f"⚠️ Primary model failed: {e}")
        try:
            return generate_with_model(FALLBACK_MODEL, user_query)
        except Exception as fallback_error:
            return f"❌ Gemini Fallback Error: {str(fallback_error)}"

if __name__ == "__main__":
    user_input = input("📝 Enter a sample user query: ")
    print("\n🤖 Gemini Reply:\n")
    print(get_gemini_reply(user_input))

