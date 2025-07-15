from flask import Flask, request
import os
import requests
from dotenv import load_dotenv
from shopify_utils import fetch_order_status_by_phone
from gemini_utils import get_gemini_reply

load_dotenv()
app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

def send_whatsapp_message(phone_number, reply_text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": reply_text}
    }
    res = requests.post(url, headers=headers, json=payload)
    print("✅ WhatsApp sent:", res.status_code, res.text)

@app.route("/webhook", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Unauthorized", 403

    try:
        data = request.get_json()
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if messages:
            msg = messages[0]
            phone_number = msg["from"]
            user_text = msg["text"]["body"].strip()
            print(f"📥 User: {user_text}")

            # INTENT FILTERS
            lowered = user_text.lower()

            if "track order" in lowered or "order status" in lowered:
                order_id = fetch_order_status_by_phone(user_text)
                reply = f"📦 Order status: {order_id}"
            elif any(word in lowered for word in ["refund", "return", "replace", "cancel"]):
                reply = "🙏 Kripya refund, return ya order issues ke liye humein email karein: support@theayurvedaco.com"
            elif any(greet in lowered for greet in ["hi", "hello", "namaste", "hey", "good morning"]):
                reply = "🙏 Namaste! Ayurvedic help chahiye toh apna health ya beauty concern likhein. TACX here to help you!"
            else:
                # Forward only genuine Ayurveda queries to Gemini
                reply = get_gemini_reply(phone_number, user_text)

            send_whatsapp_message(phone_number, reply)
        else:
            print("⚠️ No valid user message found in webhook.")

    except Exception as e:
        print("❌ Webhook Exception:", str(e))

    return "OK", 200

