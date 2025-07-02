import os
import json
import requests
from flask import Flask, request
from shopify_utils import get_order_details_by_phone, format_order_summary
from utils import match_faq_response

app = Flask(__name__)

# Load environment variables
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# Log env to verify they're loaded
print("VERIFY_TOKEN:", VERIFY_TOKEN)
print("WHATSAPP_TOKEN:", WHATSAPP_TOKEN[:4] + "..." if WHATSAPP_TOKEN else None)
print("PHONE_NUMBER_ID:", PHONE_NUMBER_ID)

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
        print("Incoming webhook payload:\n", json.dumps(data, indent=2))

        try:
            changes = data['entry'][0]['changes'][0]['value']
            messages = changes.get('messages')
            if not messages:
                print("No message found.")
                return "no message", 200

            message_data = messages[0]
            phone_number = message_data['from'][-10:]
            incoming_text = message_data.get('text', {}).get('body', "").lower()
            print("Incoming text:", incoming_text)

        except Exception as e:
            print("Webhook parsing error:", e)
            return "error", 200

        # Match FAQ
        faq_response = match_faq_response(incoming_text)
        print("FAQ matched response:", faq_response)

        if faq_response:
            send_whatsapp_message(phone_number, faq_response)
        else:
            # Fallback: Check Shopify
            shopify_response = get_order_details_by_phone(phone_number)
            print("Shopify response:", shopify_response)

            default_message = "We couldn't find any recent orders linked to this number. Please provide your order ID or contact support."

            try:
                customers = shopify_response.get("data", {}).get("customers", {}).get("nodes", [])
                orders = customers[0]["orders"]["nodes"] if customers else []
                if orders:
                    order_messages = [format_order_summary(order) for order in orders]
                    default_message = "\n\n".join(order_messages)
            except Exception as e:
                print("Error parsing Shopify orders:", e)

            send_whatsapp_message(phone_number, default_message)

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
    print("Sending message to:", phone_number)
    print("Payload:", json.dumps(payload, indent=2))

    response = requests.post(url, json=payload, headers=headers)
    print("WhatsApp API Response:", response.status_code, response.text)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
