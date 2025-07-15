import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-pro")

def get_gemini_reply(user_text):
    try:
        system_instruction = """
🔮 TACX Ayurvedic AI Support (WhatsApp Version)

You are TACX – the Ayurvedic AI Expert of The Ayurveda Co.
Respond ONLY to health, beauty & wellness topics rooted in Ayurveda × Modern Science.
Focus Areas: Doshas, skin/hair/body issues, sleep, gut, mental health, herbs, beauty, energy, immunity, etc.

❌ Do NOT reply to non-Ayurveda topics or any messages containing these keywords:
hi, hello, namaste, hey, morning, order, track, refund, coupon, thanks, ok, hmm

If non-Ayurveda: reply with:
"I'm here only to guide you on Ayurveda + Wellness topics 🙏"
"""

        contents = [
            types.Content(role="user", parts=[types.Part.from_text(user_text)]),
        ]

        response = model.generate_content(
            contents=contents,
            generation_config=types.GenerationConfig(
                temperature=0.7
            ),
            system_instruction=[types.Part.from_text(system_instruction)]
        )

        return response.text.strip()

    except Exception as e:
        print("❌ Gemini Error:", e)
        return "🙏 Sorry, I couldn't process that. Please try again."
