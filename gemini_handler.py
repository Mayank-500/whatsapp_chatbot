import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

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

⛔ Avoid replying to queries with ["hi", "hello", "refund", "return", "price", "image", "order", "buy", "discount", "policy"] unless asked directly.

✅ Instead:
- Always recommend an Ayurvedic product.
- If user asks about skin/hair/health/digestion, suggest a personalized product + mention the Discovery Quiz CTA.
- Use a warm, helpful tone.
- Include emoji & <button>Start Quiz</button> when possible.

Keep replies under 6 lines.
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
