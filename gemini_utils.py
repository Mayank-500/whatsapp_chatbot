import os
from google import genai
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

🚫 Strictly DO NOT reply to:
hi, hello, namaste, hey, morning, coupon, refund, complaint, abuse, delivery, order, track status — or any non-ayurvedic conversation.

✅ Conversational Rules:
- Keep reply short, crisp, max 6 lines
- Use Hinglish (Hindi+English), like a friendly Ayurvedic doctor
- Use creative, varied response styles (✨ emojis, ⭐ bullets, 🔗 CTA buttons)
- Maintain memory for flowing conversations
- Never sound robotic or repetitive

🧠 Smart Quiz System (Only for Body-Related Concerns):
If user talks about health/body symptoms (like hair fall, digestion, sleep, acne, weight), trigger a 3-step quiz.

⭐ Always include product recommendation like:
🧴 *Product Name*  
🔘 [🛒 Buy Now] [📖 Learn More]
        """.strip()

        response = model.generate_content(
            contents=[{
                "role": "user",
                "parts": [user_text],
            }],
            generation_config={"temperature": 0.7},
            system_instruction=system_instruction
        )

        return response.text.strip() if response.text else "🤖 Sorry, I couldn’t generate a reply. Try rephrasing?"

    except Exception as e:
        print("❌ Gemini error:", e)
        return "⚠️ Internal error with Ayurvedic assistant. Please try again later."
