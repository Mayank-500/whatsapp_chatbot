from flask import Flask, request
import requests
import json
import os
from dotenv import load_dotenv
import openai
from shopify_utils import get_latest_order_by_phone, get_order_by_id

# Load environment variables
load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
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
        user_text = message['text']['body'].lower()

        # Step 1: Try FAQ
        reply = check_faq(user_text)

        # Step 2: If no reply found, check intent
        if reply is None:
            intent = get_intent_from_gpt(user_text)

            if intent == "order":
                reply = get_latest_order_by_phone(user_id)
            elif intent == "order_id":
                reply = "Please share your Order ID (e.g. #TACX1234) to fetch details."
            elif "tacx" in user_text or "#" in user_text:
                order_id = extract_order_id(user_text)
                reply = get_order_by_id(order_id)
            else:
                reply = route_intent(intent)

            # Store for learning
            faq[user_text] = reply
            with open(FAQ_FILE, "w") as f:
                json.dump(faq, f, indent=2)

        send_whatsapp_message(user_id, reply)

    except Exception as e:
        print("Error:", e)

    return "OK", 200

# -------------------- Helper Functions --------------------
def check_faq(message):
    for category, entry in faq.items():
        if isinstance(entry, dict) and "keywords" in entry:
            for keyword in entry["keywords"]:
                if keyword in message:
                    return entry["response"]
    return None

def get_intent_from_gpt(message):
    prompt = f"What is the user's intent for: \"{message}\"? Return one: order, order_id, product, consultation, complaint, greeting, unknown."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"].strip().lower()
    except Exception as e:
        print("OpenAI error:", e)
        return "unknown"

def route_intent(intent):
    routes = {
        "product": "🛍️ Explore our Ayurveda wellness products here: https://tacx.in/shop",
        "consultation": "📞 Book your free consultation with our experts: https://tacx.in/consult",
        "complaint": "⚠️ Sorry for the trouble. Please file a complaint: https://tacx.in/support",
        "greeting": "Namaste 🙏 How can I help you today?",
    }
    return routes.get(intent, "Sorry, I didn’t understand that. Can you please rephrase?")

def extract_order_id(message):
    words = message.split()
    for word in words:
        if word.startswith("#") or word.upper().startswith("TACX"):
            return word.strip("#").strip()
    return None

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
    print("Sent:", r.status_code, r.text)

# -------------------- Start Flask App --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5057))
    app.run(host="0.0.0.0", port=port)

