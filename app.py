from flask import Flask, request
import os
import json
from dotenv import load_dotenv
from shopify_utils import fetch_order_status_by_phone
from gemini_utils import get_gemini_reply

# Load environment variables
load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid verification token", 403

    if request.method == 'POST':
        data = request.get_json()
        try:
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    if messages:
                        message = messages[0]
                        user_text = message["text"]["body"]
                        sender_id = message["from"]

                        print(f"📩 Received message: {user_text}")

                        # Fallback check: If user asks for order tracking
                        if "track" in user_text.lower():
                            order_status = fetch_order_status_by_phone(sender_id)
                            reply_text = order_status if order_status else "❌ No order found for this number."
                        else:
                            gemini_reply = get_gemini_reply(user_text)
                            reply_text = gemini_reply if gemini_reply else "🙏 I'm here only to guide you on Ayurveda + Wellness topics."

                        send_whatsapp_message(sender_id, reply_text)

        except Exception as e:
            print("❌ Webhook error:", e)

        return "OK", 200

def send_whatsapp_message(phone, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {
            "body": text
        }
    }
    response = request.post(url, headers=headers, data=json.dumps(payload))
    print(f"✅ Message sent: {response.status_code}", response.text)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
