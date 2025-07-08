import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
import traceback

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ALLOWED_KEYWORDS = [
    "ayurveda", "dosha", "kapha", "pitta", "vata", "prakriti", "nadi", "consultation",
    "herbal", "oil", "shampoo", "moisturizer", "skin", "hair", "supplement", "wellness",
    "ayurvedic", "therapy", "medicine", "natural", "treatment", "immunity", "health", "detox"
]

def is_domain_specific(question: str) -> bool:
    question = question.lower()
    return any(keyword in question for keyword in ALLOWED_KEYWORDS)

def generate_openai_response(user_message: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # ✅ downgraded from gpt-4o to save quota
            messages=[
                {"role": "system", "content": "You are an expert Ayurveda consultant. Answer in simple and helpful language."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.6
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ OpenAI API Error:", e)
        traceback.print_exc()
        return "⚠ Sorry, something went wrong while generating a response."
