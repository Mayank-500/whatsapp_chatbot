import os
from google import genai
from google.generativeai.types import Content


genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

GEMINI_KEYWORDS = {
    "products": ["kumkumadi", "shilajit", "face wash", "oil", "serum", "kit", "turmeric", "amla", "ashwagandha", "saffron", "hair oil"],
    "wellness": ["stress", "digestion", "sleep", "immunity", "skin glow", "pimples", "ayurveda", "dosha"],
    "offers": ["offer", "discount", "deal", "combo"],
    "quiz": ["start quiz", "discovery quiz", "dosha", "quiz"]
}

def smart_gemini_reply(user_message):
    user_msg = user_message.lower()

    # Fast keyword reply
    for topic, keywords in GEMINI_KEYWORDS.items():
        if any(keyword in user_msg for keyword in keywords):
            return predefined_response(topic)

    # Fallback to Gemini AI
    response = model.generate_content([Content(parts=[user_message])])
    return response.text.strip()

def predefined_response(topic):
    if topic == "products":
        return (
            "🌸 We offer Ayurvedic gems like *Kumkumadi Face Wash*, *Shilajit Resin*, and *Ashwagandha Tablets*.\n"
            "Explore → https://tacx.in/collections/all"
        )
    elif topic == "wellness":
        return (
            "🌿 Ayurveda helps balance your body using herbs like Ashwagandha (for stress), Triphala (digestion), "
            "and Amla (immunity).\nNeed something specific?"
        )
    elif topic == "offers":
        return (
            "🎁 We have great deals on Ayurvedic kits!\nSee all offers → https://tacx.in/collections/combo-offers"
        )
    elif topic == "quiz":
        return (
            "✨ Our Discovery Quiz helps find Ayurvedic solutions just for you.\nType *Start Quiz* to begin!"
        )
    else:
        return "🙏 I'm here to guide you with Ayurveda-based wellness tips. Ask me anything!"
