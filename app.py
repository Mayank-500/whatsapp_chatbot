from flask import Flask, request
import requests
import json
import os
import re
from dotenv import load_dotenv
import openai
from shopify_utils import fetch_order_status_by_phone

# Load environment variables
load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

openai.api_key = OPENAI_API_KEY

# Load FAQ
FAQ_FILE = "faq.json"
faq = {}
if os.path.exists(FAQ_FILE):
    with open(FAQ_FILE, "r") as f:
        faq = json.load(f)

# Load Keywords
KEYWORDS_FILE = "keywords.json"
keywords = []
if os.path.exists(KEYWORDS_FILE):
    with open(KEYWORDS_FILE, "r") as f:
        keywords = json.load(f)["keywords"]

# Load Core Product Map
PRODUCT_MAP_FILE = "core_key_to_product.json"
core_product_map = {}
if os.path.exists(PRODUCT_MAP_FILE):
    with open(PRODUCT_MAP_FILE, "r") as f:
        core_product_map = json.load(f)

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_id = message['from']

        if 'text' not in message:
            print("⚠️ Non-text message received")
            return "OK", 200

        user_text = message['text']['body'].lower()
        print("📩 Message:", user_text)

        phone = extract_phone_number(user_text)
        if phone:
            reply = fetch_order_status_by_phone(phone)
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        reply = check_faq(user_text)

        if reply is None:
            if any(keyword in user_text for keyword in keywords):
                reply = get_openai_reply(user_text)

                # Attach related product
                for keyword in core_product_map:
                    if keyword in user_text:
                        reply += f"\n\n🛍️ Related product: {core_product_map[keyword]}"
                        break
            else:
                reply = "🙏 I'm here to assist with Ayurveda-based products, orders, and consultations. Please ask related queries."

        send_whatsapp_message(user_id, reply)

    except Exception as e:
        print("❌ Webhook error:", e)

    return "OK", 200

def extract_phone_number(message):
    match = re.search(r"\b\d{10}\b", message)
    return "+91" + match.group() if match else None

def check_faq(message):
    for _, entry in faq.items():
        for keyword in entry["keywords"]:
            if keyword.lower() in message:
                return entry["response"]
    return None

def get_openai_reply(user_text):
    prompt = f"You are an Ayurvedic product expert from The Ayurveda Co. Answer briefly: \"{user_text}\""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print("❌ OpenAI error:", e)
        return "🤖 I’m still learning. Try again later."

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
    requests.post(WHATSAPP_API_URL, headers=headers, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
