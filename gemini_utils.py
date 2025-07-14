import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")  # or "gemini-pro" as fallback

# Gemini reply function
def get_gemini_reply(user_text):
    try:
        # Define system behavior
        system_instruction = """
🔮 TACX Ayurvedic AI Support (WhatsApp Version)

You are TACX – the Ayurvedic AI Expert of The Ayurveda Co.
Respond ONLY to questions related to Ayurveda × Science such as doshas, herbs, immunity, beauty, gut health, sleep, mental clarity, hair/skin/body issues and anything that surrounds the company and Ayurvedic health.

❌ Do NOT reply to non-Ayurveda topics or any general greetings like:
hi, hello, namaste, hey, morning etc.
"""

        # Create a new chat session with initial system prompt
        chat = model.start_chat(history=[
            {"role": "system", "parts": [system_instruction]},
        ])

        # Send user's message and receive AI reply
        response = chat.send_message(user_text)

        # Return clean text
        return response.text.strip()

    except Exception as e:
        return f"❌ Gemini Error: {str(e)}"
