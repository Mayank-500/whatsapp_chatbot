import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use the new Gemini 2.5 Flash model (fast + smart)
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-pro"

def get_gemini_reply(user_text):
    system_instruction = """
🔮 TACX Ayurvedic AI Support (WhatsApp Version)

You are TACX – the Ayurvedic AI Expert of The Ayurveda Co.
Respond ONLY to questions related to Ayurveda × Science such as doshas, herbs, immunity, beauty, gut health, sleep, mental clarity, hair/skin/body issues and anything that surrounds the company and Ayurvedic health.

❌ Do NOT reply to non-Ayurveda topics or any general greetings like:
hi, hello, namaste, hey, morning etc.
"""

    def generate_reply(model_name):
        model = genai.GenerativeModel(model_name)
        chat = model.start_chat(history=[
            {"role": "system", "parts": [system_instruction]},
        ])
        return chat.send_message(user_text).text.strip()

    try:
        return generate_reply(PRIMARY_MODEL)

    except Exception as e:
        print(f"⚠️ Primary model ({PRIMARY_MODEL}) failed: {e}")
        if "429" in str(e):
            return "⚠️ We're currently handling too many requests. Please try again shortly."
        try:
            return generate_reply(FALLBACK_MODEL)
        except Exception as fallback_error:
            return f"❌ Gemini Fallback Error: {str(fallback_error)}"
