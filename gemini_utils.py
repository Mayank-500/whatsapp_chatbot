# pip install google-generativeai
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

PRIMARY_MODEL = "models/gemini-2.5-flash"
FALLBACK_MODEL = "models/gemini-pro"

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
If user talks about health/body symptoms (like hair fall, digestion, sleep, acne, weight), trigger a **3-step interactive quiz** to identify exact concern:
  - Step 1: Ask 3 possible types of the problem
  - Step 2: User replies with number (1, 2, or 3)
  - Step 3: Give smart Ayurvedic product recommendation based on the selection
🛑 Do NOT run quiz on non-body topics like: tulsi benefits, what is triphala, etc.
❌ Do NOT say “Start Quiz” again and again – show only once, and don’t follow up if ignored.
⛔ Do not repeat earlier steps or explanations after Step 3.

📸 For every reply, ALWAYS end with:

⭐ Recommended TACX Product:  
🧴 *Product Name*  
🔘 [🛒 Buy Now] [📖 Learn More]

🎁 If applicable, show Combo Offers from curated `combo.json` list
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
            print(f"❌ Fallback model failed: {fallback_error}")
            return "⚠️ Gemini AI error. Please try again later."

# Optional test
if __name__ == "__main__":
    user_input = input("📝 Enter a sample user query: ")
    print("\n🤖 Gemini Reply:\n")
    print(get_gemini_reply(user_input))
