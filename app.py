from flask import Flask, request
import requests
import os
import json
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# Load faq.json
faq = {}
FAQ_FILE = "faq.json"
if os.path.exists(FAQ_FILE):
    with open(FAQ_FILE, "r") as f:
        faq = json.load(f)
        print("✅ FAQ loaded:", list(faq.keys()))
else:
    print("❌ faq.json not found")

# WhatsApp send API
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

# -------------------------------------
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# -------------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📥 Incoming POST:", json.dumps(data, indent=2))

    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_id = message['from']

        if 'text' not in message:
            print("⚠️ Non-text message")
            return "OK", 200

        user_text = message['text']['body'].lower()
        print("📩 Received:", user_text)

        reply = match_faq(user_text)

        if reply:
            send_whatsapp_message(user_id, reply)
        else:
            send_whatsapp_message(user_id, "🙏 Sorry, I didn't understand. Please ask about consultation, orders, or products.")

    except Exception as e:
        print("❌ Error:", e)

    return "OK", 200

# -------------------------------------
def match_faq(user_text):
    for category, entry in faq.items():
        keywords = entry.get("keywords", [])
        for keyword in keywords:
            if keyword in user_text:
                print(f"✅ Matched '{keyword}' in '{category}'")
                return entry.get("response")
    print("❌ No FAQ match")
    return None

def send_whatsapp_message(to, message):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print("📤 WhatsApp API:", response.status_code, response.text)

# -------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
