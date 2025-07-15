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

# In-memory user session storage
user_sessions = {}

# Load FAQ
FAQ_FILE = "faq.json"
faq = {}
if os.path.exists(FAQ_FILE):
    with open(FAQ_FILE, "r") as f:
        faq = json.load(f)

# Webhook verification
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# Webhook message handler
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_id = message['from']

        if 'text' not in message:
            print("⚠️ Non-text message received:", message)
            return "OK", 200

        user_text = message['text']['body'].strip()
        print("📩 Received:", user_text)

        phone = extract_phone_number(user_text)
        if phone:
            reply = fetch_order_status_by_phone(phone)
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        # Check quiz stage
        session = user_sessions.get(user_id, {})
        last_stage = session.get("stage")
        last_symptom = session.get("symptom")

        # User replies 1/2/3 during a quiz
        if last_stage == "quiz" and re.fullmatch(r"[1-3]", user_text):
            combined_input = f"{last_symptom.strip()} - Option: {user_text.strip()}"
            reply = get_gemini_reply(combined_input)
            send_whatsapp_message(user_id, reply)
            user_sessions[user_id] = {"stage": "complete", "symptom": last_symptom}
            return "OK", 200

        # FAQ fallback
        faq_reply = check_faq(user_text.lower())
        if faq_reply:
            send_whatsapp_message(user_id, faq_reply)
            return "OK", 200

        # AI reply
        ai_reply = get_gemini_reply(user_text)

        # Store state if it starts a quiz
        if "quiz karte hain" in ai_reply or "quiz karte hai" in ai_reply:
            user_sessions[user_id] = {"stage": "quiz", "symptom": user_text}

        send_whatsapp_message(user_id, ai_reply)

    except Exception as e:
        print("❌ Webhook error:", e)

    return "OK", 200

# Helper: Phone extraction
def extract_phone_number(message):
    match = re.search(r"\b\d{10}\b", message)
    if match:
        return "+91" + match.group()
    return None

# Helper: FAQ check
def check_faq(message):
    for category, entry in faq.items():
        if isinstance(entry, dict) and "keywords" in entry:
            for keyword in entry["keywords"]:
                if keyword.lower() in message:
                    return entry.get("response")
    return None

# Helper: Send message
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
    print("✅ Sent:", r.status_code, r.text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

