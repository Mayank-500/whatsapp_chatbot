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

# Load local data files
with open("faq.json", "r") as f:
    faq = json.load(f)

with open("keywords.json", "r") as f:
    keywords_map = json.load(f)

with open("core_key_to_product.json", "r") as f:
    product_links = json.load(f)

# -------------------- Webhook Verification --------------------
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# -------------------- WhatsApp Message Handler --------------------
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

        # 📦 Step 0: Order tracking via phone number
        phone = extract_phone_number(user_text)
        if phone:
            reply = fetch_order_status_by_phone(phone)
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        # 📚 Step 1: Static FAQ check
        faq_reply = check_faq(user_text)
        if faq_reply:
            send_whatsapp_message(user_id, faq_reply)
            return "OK", 200

        # 🧠 Step 2: Keyword match + AI + Product suggestion
        keyword_hit = match_keyword(user_text)
        if keyword_hit:
            reply = generate_gpt_response(user_text)
            product_suggestion = suggest_product(keyword_hit)
            full_reply = reply + ("\n\n🌿 *Recommended for you:*\n" + product_suggestion if product_suggestion else "")
            send_whatsapp_message(user_id, full_reply)
            return "OK", 200

        # 🤖 Step 3: Fallback for unrelated queries
        send_whatsapp_message(user_id, "🙏 I'm here to help with products, wellness advice, and orders. Please ask a relevant Ayurveda-related question.")
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
    for _, entry in faq.items():
        if "keywords" in entry:
            for keyword in entry["keywords"]:
                if keyword.lower() in message:
                    return entry["response"]
    return None

def match_keyword(message):
    for category, keys in keywords_map.items():
        for key in keys:
            if key.lower() in message:
                return key.lower()
    return None

def suggest_product(keyword):
    product = product_links.get(keyword)
    if product:
        return f"{product['product']} 👉 {product['link']}"
    return None

def generate_gpt_response(message):
    prompt = f"As an expert in Ayurveda from The Ayurveda Co., briefly answer this user question:\n\n\"{message}\""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print("❌ OpenAI error:", e)
        return "🙏 Sorry, I couldn't process that. Please ask again later."

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
