import os
from flask import Flask, request
import requests
import json
from shopify_utils import get_order_details_by_phone, format_order_summary

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "nishu")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")  # ⚠️ You must set this in Render env

# Load FAQ from JSON
with open("faq.json", "r") as f:
    faq_data = json.load(f)


def match_faq_response(message):
    message_lower = message.lower()
    for category, data in faq_data.items():
        if any(keyword in message_lower for keyword in data["keywords"]):
            return data["response"]
    return None


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
        print("🔔 Incoming webhook:", json.dumps(data, indent=2))

        try:
            incoming_message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
            phone_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from'][-10:]
            print(f"📞 Extracted phone: {phone_number}")
            print(f"💬 User message: {incoming_message}")
        except Exception as e:
            print(f"🚨 Error parsing message: {e}")
            return "error", 200

        # Step 1: FAQ response
        matched = match_faq_response(incoming_message)
        print("📚 Matched FAQ response:", matched)

        if matched:
            send_whatsapp_message(phone_number, matched)
            return "ok", 200

        # Step 2: Shopify order lookup fallback
        shopify_response = get_order_details_by_phone(phone_number)
        print("📦 Shopify response:", shopify_response)

        message_to_send = "❗We couldn’t find any recent orders linked to this number. Please share your order ID or try again later."

        try:
            customers = shopify_response.get("data", {}).get("customers", {}).get("nodes", [])
            if customers and customers[0]["orders"]["nodes"]:
                orders = customers[0]["orders"]["nodes"]
                message_to_send = "\n\n".join(format_order_summary(order) for order in orders)
        except Exception as e:
            print(f"❌ Shopify response parsing error: {e}")

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
    print("📤 Sending to WhatsApp:", json.dumps(payload, indent=2))
    res = requests.post(url, json=payload, headers=headers)
    print("📬 WhatsApp API response:", res.status_code, res.text)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
