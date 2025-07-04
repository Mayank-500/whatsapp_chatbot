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

# Load FAQ and keywords
FAQ_FILE = "faq.json"
KEYWORDS_FILE = "keywords.json"
PRODUCT_MAP_FILE = "core_key_to_product.json"

faq = {}
keywords = []
product_map = {}

if os.path.exists(FAQ_FILE):
    with open(FAQ_FILE, "r") as f:
        faq = json.load(f)

if os.path.exists(KEYWORDS_FILE):
    with open(KEYWORDS_FILE, "r") as f:
        keywords = json.load(f).get("keywords", [])

if os.path.exists(PRODUCT_MAP_FILE):
    with open(PRODUCT_MAP_FILE, "r") as f:
        product_map = json.load(f)

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

        if 'text' not in message:
            print("⚠️ Non-text message received:", message)
            return "OK", 200

        user_text = message['text']['body'].lower()
        print("📩 Received message:", user_text)

        # Step 0: Check for phone number to track order
        phone = extract_phone_number(user_text)
        if phone:
            reply = fetch_order_status_by_phone(phone)
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        # Step 1: Check FAQ
        reply = check_faq(user_text)
        print("📚 FAQ reply:", reply)

        # Step 2: Use GPT for company-specific questions
        if reply is None and contains_keyword(user_text):
            answer = get_answer_from_gpt(user_text)
            product_suggestion = suggest_product(user_text)
            reply = answer
            if product_suggestion:
                reply += f"\n\n🛍️ Related Product: {product_suggestion}"

        if reply:
            send_whatsapp_message(user_id, reply)
        else:
            send_whatsapp_message(user_id, "🙏 Sorry, I didn't understand. Please ask about consultation, products, or orders.")

    except Exception as e:
        print("❌ Webhook error:", e)

    return "OK", 200

# -------------------- Helper Functions --------------------
def extract_phone_number(message):
    match = re.search(r"\b\d{10}\b", message)
    if match:
        return "+91" + match.group()
    return None

def check_faq(message):
    for category, entry in faq.items():
        if isinstance(entry, dict) and "keywords" in entry:
            for keyword in entry["keywords"]:
                if keyword.lower() in message:
                    return entry.get("response")
    return None

def contains_keyword(message):
    return any(keyword.lower() in message for keyword in keywords)

def suggest_product(message):
    for key, url in product_map.items():
        if key.lower() in message:
            return url
    return None

def get_answer_from_gpt(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in Ayurveda answering questions for The Ayurveda Co. Keep it short and helpful."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print("❌ OpenAI error:", e)
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

# -------------------- Run App --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
