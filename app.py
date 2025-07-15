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

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid verification token", 403

    data = request.get_json()
    print(json.dumps(data, indent=2))

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages")

        if not messages:
            print("❌ Webhook Exception: 'messages' not found")
            return "ok", 200

        phone_number = value["contacts"][0]["wa_id"]
        user_text = messages[0]["text"]["body"].strip()
        print(f"📥 User: {user_text}")

        # Order tracking if phone number format detected
        match = re.search(r"\b(7\d{9}|8\d{9}|9\d{9})\b", user_text)
        if match:
            order_status = fetch_order_status_by_phone(match.group())
            reply = order_status
        else:
            reply = get_gemini_reply(phone_number, user_text)

        # Send reply back
        url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": reply},
        }
        res = requests.post(url, headers=headers, json=payload)
        print("✅ WhatsApp sent:", res.status_code, res.text)

    except Exception as e:
        print("❌ Webhook Exception:", e)

    return "ok", 200

@app.route("/")
def home():
    return "TACX WhatsApp AI Bot is running!"
