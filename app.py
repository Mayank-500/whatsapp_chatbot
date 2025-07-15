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

@app.route('/')
def home():
    return "🌿 TACX Ayurvedic AI Bot is running."

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "❌ Invalid verification token"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("📩 Received message:", json.dumps(data, indent=2))

        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                if not messages:
                    print("❌ Webhook warning: No messages found.")
                    continue

                for message in messages:
                    phone_number = value.get("metadata", {}).get("display_phone_number", "")
                    user_id = message.get("from")
                    user_text = message.get("text", {}).get("body", "").strip()

                    # Handle order tracking keywords
                    if re.search(r"\b(order|track|refund)\b", user_text.lower()):
                        phone_match = re.search(r'\d{10}', user_text)
                        if phone_match:
                            phone_number = phone_match.group()
                            order_status = fetch_order_status_by_phone(phone_number)
                            reply_text = order_status or "❌ No order found with this number."
                        else:
                            reply_text = "📦 Please share your 10-digit phone number to track the order."
                    else:
                        # Otherwise handle via Gemini AI
                        reply_text = get_gemini_reply(user_text)

                    send_whatsapp_message(user_id, reply_text)

    except Exception as e:
        print("❌ Webhook error:", e)

    return "OK", 200

def send_whatsapp_message(recipient_id, message):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("✅ Message sent:", response.status_code, response.text)

if __name__ == '__main__':
    app.run(port=5000, debug=True)

