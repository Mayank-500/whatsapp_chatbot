# pip install google-genai python-dotenv

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API key from .env
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise EnvironmentError("❌ GEMINI_API_KEY is missing in your .env file.")

# Create Gemini client
client = genai.Client(api_key=api_key)

# TACX system instruction
system_instruction = """
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

⭐ Recommended TACX Product:  
🧴 *Product Name*  
🔘 [🛒 Buy Now] [📖 Learn More]

🎁 If applicable, show Combo Offers from curated `combo.json` list
""".strip()

# Core response function
def get_gemini_reply(user_input):
    try:
        model = "gemini-2.5-flash"

        contents = [
            types.Content(
                role="user",
                parts=[types.Part(text=user_input)]
            )
        ]

        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            response_mime_type="text/plain",
            system_instruction=[types.Part(text=system_instruction)]
        )

        print("🤖 TACX AI replying...\n")
        full_response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        ):
            full_response += chunk.text
        return full_response.strip()

    except Exception as e:
        print("❌ Gemini error:", e)
        return "⚠️ Internal error with Ayurvedic assistant. Please try again later."

# Run standalone
if __name__ == "__main__":
    user_input = input("Ask TACX something Ayurvedic: ")
    reply = get_gemini_reply(user_input)
    print("\n" + reply)
