from flask import Flask, request
import os, json, re
import requests  
from dotenv import load_dotenv
from shopify_utils import fetch_order_status_by_phone
from gemini_utils import get_gemini_reply

load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

FAQ_FILE = "faq.json"
faq = {}
if os.path.exists(FAQ_FILE):
    with open(FAQ_FILE, "r") as f:
        faq = json.load(f)

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
            return "OK", 200
        user_text = message['text']['body'].strip()
        print("📥 User:", user_text)

        # Check if phone number for order tracking
        phone = extract_phone_number(user_text)
        if phone:
            reply = fetch_order_status_by_phone(phone)
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        # Check for FAQ keywords
        faq_reply = check_faq(user_text.lower())
        if faq_reply:
            send_whatsapp_message(user_id, faq_reply)
            return "OK", 200

        # Ayurveda Gemini AI flow
        reply = get_gemini_reply(user_id, user_text)
        send_whatsapp_message(user_id, reply)
    except Exception as e:
        print("❌ Webhook Exception:", e)

    return "OK", 200

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
    res = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print("✅ WhatsApp sent:", res.status_code, res.text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
