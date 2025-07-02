import os
from flask import Flask, request
import requests
from shopify_utils import get_order_details_by_phone, format_order_summary
import json

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "nishu")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

# Load FAQ intents from JSON
with open("faq.json", "r") as f:
    faq_data = json.load(f)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    if request.method == 'POST':
        data = request.get_json()
        print("🔔 Incoming webhook:", data)

        try:
            message_text = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'].lower()
            phone_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from'][-10:]
            print(f"📞 Final phone number used: {phone_number}")
        except Exception as e:
            print(f"🚨 Error in webhook: {e}")
            return "error", 200

        # Check for FAQ match
        for intent in faq_data.values():
            for keyword in intent['keywords']:
                if keyword.lower() in message_text:
                    send_whatsapp_message(phone_number, intent['response'])
                    return "ok", 200

        # If not FAQ, check Shopify orders
        shopify_response = get_order_details_by_phone(phone_number)
        print("📦 Shopify response:\n", shopify_response)

        message_to_send = "❗We couldn’t find any recent orders linked to this number. Please share your order ID or try again later."

        try:
            orders = (
                shopify_response["data"]["customers"]["nodes"][0]["orders"]["nodes"]
                if shopify_response.get("data") and shopify_response["data"]["customers"]["nodes"]
                else []
            )

            if orders:
                message_to_send = "\n\n".join(format_order_summary(order) for order in orders)
        except Exception as e:
            print(f"❌ Shopify Error: {e}")

        send_whatsapp_message(phone_number, message_to_send)
        return "ok", 200


def send_whatsapp_message(phone_number, message):
    payload = {
        "messaging_product": "whatsapp",
        "to": f"91{phone_number}",
        "type": "text",
        "text": {"body": message}
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    res = requests.post(
        "https://graph.facebook.com/v18.0/YOUR_PHONE_NUMBER_ID/messages",
        json=payload,
        headers=headers
    )
    print("📤 Sent to WhatsApp:", res.status_code, res.text)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
