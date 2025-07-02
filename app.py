from flask import Flask, request
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

# Load static FAQ from faq.json
FAQ_FILE = "faq.json"
faq = {}
if os.path.exists(FAQ_FILE):
    with open(FAQ_FILE, "r") as f:
        faq = json.load(f)
    print("✅ FAQ loaded:", list(faq.keys()))
else:
    print("❌ faq.json not found!")

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
            print("⚠️ Ignoring non-text message.")
            return "OK", 200

        user_text = message['text']['body'].lower().strip()
        print("📩 Received message:", user_text)

        # Match message with FAQ keywords
        reply = match_faq(user_text)

        if reply:
            send_whatsapp_message(user_id, reply)
            print("✅ Sent FAQ reply.")
        else:
            send_whatsapp_message(user_id, "🙏 Sorry, I couldn’t find an answer to that. Please ask about consultation, products, or orders.")
            print("⚠️ No FAQ match found.")

    except Exception as e:
        print("❌ Webhook error:", e)

    return "OK", 200

# -------------------- FAQ Matching Logic --------------------
def match_faq(message):
    for category, entry in faq.items():
        if "keywords" in entry:
            for keyword in entry["keywords"]:
                if keyword.lower() in message:
                    print(f"🔍 Matched keyword '{keyword}' in category '{category}'")
                    return entry.get("response")
    return None

# -------------------- WhatsApp Send Function --------------------
def send_whatsapp_message(to, message):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    r = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print("📬 WhatsApp API response:", r.status_code, r.text)

# -------------------- Run the Flask App --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
