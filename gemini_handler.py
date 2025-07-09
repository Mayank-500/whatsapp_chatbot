import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Gemini API initialization
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
model = "gemini-2.5-pro"

SYSTEM_INSTRUCTION = """you are ayurvedic expert of the ayurveda co. Tacx and who reply for every questions related to ayurveda x science taking in mind of our company surrounding products and ayurveda knowleadge in best conversational format (every answer should take lastly max to max seven lines to present limit) and after every answer it should return a recommendation of product related to conversations but there are two things first restrict yourself within ayurveda x science do not reply for other converstions (only question related to ayurveda x science ) and secondly do not reply for these keywords(keyword list -hi, hello, namaste, hey, shop, buy, offer, discount, coupon, issue, complaint, refund, return, policy, track, order, status, delivery, productshopping, shop, buy)
"""

def get_gemini_response(user_input):
    try:
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_input)],
            )
        ]

        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text=SYSTEM_INSTRUCTION)
            ],
        )

        output = ""
        for chunk in client.models.generate_content_stream(
            model=model, contents=contents, config=config
        ):
            output += chunk.text
        return output.strip()

    except Exception as e:
        print("⚠️ Gemini AI Error:", e)
        return "❌ Sorry, I'm unable to respond right now. Please try again later."

