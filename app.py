from flask import Flask, request
import requests
import json
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

openai.api_key = OPENAI_API_KEY

# Load FAQ data
FAQ_FILE = "faq.json"
faq = {}
if os.path.exists(FAQ_FILE):
    with open(FAQ_FILE, "r") as f:
        faq = json.load(f)

# -------------------- Webhook Verification --------------------
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# -------------------- Webhook for WhatsApp Messages --------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_id = message['from']

        # Only proceed if it's a text message
        if 'text' not in message:
            print("⚠️ Non-text message received:", message)
            return "OK", 200

        user_text = message['text']['body'].lower()
        print("📩 Received message:", user_text)

        # Step 1: Check static FAQ
        reply = check_faq(user_text)
        print("📚 FAQ reply:", reply)

        # Step 2: Use GPT fallback if not found
        if reply is None:
            intent = get_intent_from_gpt(user_text)
            print("🧠 GPT-detected intent:", intent)
            reply = route_intent(intent)

            # Save unknown to faq for future learning
            faq[user_text] = {
                "keywords": [user_text],
                "response": reply
            }
            with open(FAQ_FILE, "w") as f:
                json.dump(faq, f, indent=2)

        # Step 3: Send the response
        if reply:
            send_whatsapp_message(user_id, reply)
        else:
            send_whatsapp_message(user_id, "🙏 Sorry, I didn't understand. Please ask about consultation, products, or orders.")

    except Exception as e:
        print("❌ Webhook error:", e)

    return "OK", 200

# -------------------- Helper Functions --------------------

def check_faq(message):
    for category, entry in faq.items():
        if isinstance(entry, dict) and "keywords" in entry:
            for keyword in entry["keywords"]:
                if keyword.lower() in message:
                    return entry.get("response")
    return None

def get_intent_from_gpt(message):
    prompt = f"What is the user's intent for this message: \"{message}\"? Return one of the following categories: order, product, consultation, complaint, greeting, unknown."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        intent = response.choices[0].message["content"].strip().lower()
        return intent
    except Exception as e:
        print("❌ OpenAI error:", e)
        return "unknown"

def route_intent(intent):
    if intent == "order":
        return "📦 You can track your order here: https://tacx.in/track-order"
    elif intent == "product":
        return "🛍️ Explore our Ayurvedic products: https://tacx.in/shop"
    elif intent == "consultation":
        return "🧘 Book a free consultation with our Ayurveda expert: https://tacx.in/consult"
    elif intent == "complaint":
        return "😞 We're sorry to hear that. Please raise your complaint here: https://tacx.in/support"
    elif intent == "greeting":
        return "🙏 Namaste! How can I assist you on your wellness journey today?"
    else:
        return "🤖 I'm still learning. Please ask about products, consultations, or orders."

def send_whatsapp_message(to, message):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    r = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print("✅ Message sent:", r.status_code, r.text)

# -------------------- Start Flask App --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
