import os
import re
import google.generativeai as genai
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-pro")
user_memory = defaultdict(list)
user_context = defaultdict(dict)

SYSTEM_PROMPT = """
🔮 You are TACX – the friendly Ayurvedic AI Expert of The Ayurveda Co., trained in Ayurveda × Modern Science.

🎯 Your ONLY goal is to reply to health, beauty & wellness topics rooted in Ayurveda. Focus areas:
- Doshas (Vata, Pitta, Kapha), Gut Health, Sleep, Mental Clarity
- Skin, Hair, Body issues
- Herbs, Remedies, Detox, Energy, Immunity, Women's Wellness, Beauty rituals

🚫 STRICTLY IGNORE unrelated topics like:
"hi", "hello", "coupon", "order", "track", "refund", "thanks", "ok", "abuse", etc.
→ Reply: *"I'm here only to guide you on Ayurveda + Wellness topics 🙏"*

🧠 QUIZ FLOW (Trigger only ONCE for body issues like hair fall, acne, digestion):
1. Ask about the type of issue (give 3 options)
2. Wait for reply (1/2/3)
3. Recommend solution + product + combo

🗣️ Style:
- Hinglish tone
- Max 6 lines
- Vary response style: emojis, Hinglish, nuskha, etc.
- Memory-aware (continue previous topic if user comes back)

🤫 [NOTE: Avoid repeating self-introductions if already in conversation.]
"""

def get_gemini_reply(user_text, user_id=None):
    try:
        if user_id:
            memory = user_memory[user_id]
            context = user_context[user_id]
        else:
            memory = []
            context = {}

        user_text_clean = user_text.lower().strip()
        memory.append(user_text)

        # Track last product mentioned
        product_keywords = {
            "kajal": "Ayurvedic Black Kajal",
            "kumkumadi": "Kumkumadi Face Wash",
            "oil": "Ayurvedic Hair Oil",
            "serum": "Glow Boosting Face Serum",
            "shampoo": "Onion Hair Shampoo"
        }
        
        for keyword, product in product_keywords.items():
            if keyword in user_text_clean:
                context["last_product"] = product
                break

        # Compose prompt with memory context
        prompt_parts = [SYSTEM_PROMPT]
        prompt_parts.extend(memory[-10:])
        prompt_parts.append(user_text)

        response = model.generate_content(
            prompt_parts,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7
            )
        )
        
        reply = response.text.strip()
        memory.append(reply)
        return reply

    except Exception as e:
        print("❌ Gemini Error:", e)
        return "Sorry, I'm having trouble processing your request. Please try again later."
