# gemini_handler.py

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# ✅ Set GOOGLE_API_KEY environment variable manually
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key

def smart_gemini_reply(user_message):
    try:
        model = "gemini-2.5-pro"
        client = genai.Client()

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)],
            )
        ]

        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text="""
You are an Ayurvedic expert at The Ayurveda Co. (TACX), trained to answer only queries related to Ayurveda x Science.
⛔ Do NOT reply to questions containing words like:
["hi", "hello", "namaste", "hey", "shop", "discount", "coupon", "issue", "complaint", "refund", "return", "policy", "track", "order", "status", "delivery", "buy"]

✅ Instead:
- Keep answers under 7 lines.
- Always include an Ayurvedic product recommendation (name + short benefit).
- If question is about wellness, skin, hair, herbs, body type, etc., answer smartly.
- Offer a Discovery Quiz journey with options like: Start Quiz, Skip.
- Avoid price or shopping queries directly, but you can mention benefits of products.

Respond like a friendly, knowledgeable Ayurvedic assistant in a conversational tone with emoji and buttons.
""")
            ],
        )

        response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        ):
            response += chunk.text

        return response.strip()

    except Exception as e:
        print("❌ Gemini error:", e)
        return "⚠️ Sorry, I couldn’t understand that. Please ask about Ayurvedic wellness, herbs, or skincare."
