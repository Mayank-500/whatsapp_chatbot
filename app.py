from flask import Flask, request
import requests
import json
import os
import re
from dotenv import load_dotenv
from shopify_utils import fetch_order_status_by_phone
from gemini_utils import get_gemini_reply

# Load environment variables
load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

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

# -------------------- WhatsApp Webhook Handler --------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data['entry'][0]['changes'][0]['value'].get('messages', [])[0]
        user_id = message['from']

        if 'text' not in message:
            print("⚠️ Non-text message received:", message)
            return "OK", 200

        user_text = message['text']['body'].lower()
        print("📩 Received message:", user_text)

        # 1. Shopify Order Lookup
        phone = extract_phone_number(user_text)
        if phone:
            reply = fetch_order_status_by_phone(phone)
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        # 2. FAQ Check
        reply = check_faq(user_text)
        if reply:
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        # 3. Gemini AI Reply
        gemini_reply = get_gemini_reply(user_text)
        send_whatsapp_message(user_id, gemini_reply)

    except Exception as e:
        print("❌ Webhook error:", e)

    return "OK", 200

# -------------------- Helper Functions --------------------
def extract_phone_number(message):
    cleaned = re.sub(r"[^\d]", "", message)
    match = re.search(r"\b\d{10}\b", cleaned[-10:])
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
    if r.status_code == 200:
        print("✅ Message sent successfully")
    else:
        print("❌ WhatsApp send error:", r.status_code, r.text)

# -------------------- Start Server --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
