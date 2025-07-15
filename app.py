from flask import Flask, request
import requests
import json
import os
import re
from dotenv import load_dotenv
from shopify_utils import fetch_order_status_by_phone
from gemini_utils import get_gemini_reply
from recommendation_utils import get_product_recommendation

# Load environment variables
load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Load FAQ data
with open('faq.json') as f:
    FAQ_DATA = json.load(f)

@app.route('/')
def home():
    return "🌿 TACX Ayurvedic AI Bot is running."

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "❌ Invalid verification token"

def check_faq(user_text):
    """Check if user query matches any FAQ"""
    user_text = user_text.lower().strip()
    for faq in FAQ_DATA.values():
        for keyword in faq['keywords']:
            if keyword in user_text:
                return faq['response']
    return None

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

                    # First check FAQ
                    faq_response = check_faq(user_text)
                    if faq_response:
                        send_whatsapp_message(user_id, faq_response)
                        continue

                    # Handle order tracking
                    if re.search(r"\b(order|track|refund)\b", user_text.lower()):
                        phone_match = re.search(r'\d{10,13}', user_text)
                        if phone_match:
                            number = phone_match.group()[-10:]
                            order_status = fetch_order_status_by_phone(number)
                            reply_text = order_status or "❌ No order found with this number."
                        else:
                            reply_text = "📦 Please share your 10-digit phone number to track the order."
                    # Handle product recommendations
                    elif any(keyword in user_text.lower() for keyword in 
                            ["product", "buy", "recommend", "suggest", "shampoo", "oil", 
                             "serum", "cream", "kumkumadi", "kajal", "face wash"]):
                        reply_text = get_product_recommendation(user_text)
                    else:
                        # Otherwise handle via Gemini AI
                        reply_text = get_gemini_reply(user_text, user_id)

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
