import os
from flask import Flask, request
import requests
from shopify_utils import get_order_details_by_phone, format_order_summary

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "nishu")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "YOUR_PHONE_NUMBER_ID")  # ✅ update this in your .env

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
            phone_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from'][-10:]
            print(f"📞 Final phone number used: {phone_number}")
        except Exception as e:
            print(f"🚨 Error in webhook: {e}")
            return "error", 200

        shopify_response = get_order_details_by_phone(phone_number)
        print("📦 Shopify response:", shopify_response)

        message_to_send = "❗We couldn’t find any recent orders linked to this number. Please share your order ID or try again later."

        try:
            customer_nodes = shopify_response.get("data", {}).get("customers", {}).get("nodes", [])
            orders = customer_nodes[0]["orders"]["nodes"] if customer_nodes and customer_nodes[0]["orders"]["nodes"] else []
            if orders:
                message_to_send = "\n\n".join(format_order_summary(order) for order in orders)
        except Exception as e:
            print(f"❌ Shopify formatting error: {e}")

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

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    res = requests.post(url, json=payload, headers=headers)
    print("📤 Sent to WhatsApp:", res.status_code, res.text)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
