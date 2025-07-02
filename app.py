import os
from flask import Flask, request
import requests
from shopify_utils import get_order_details_by_phone, format_order_summary
from utils import match_faq_response

app = Flask(__name__)

# Environment variables
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Handle webhook verification from Meta
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    if request.method == 'POST':
        data = request.get_json()
        print("Incoming webhook payload:", data)

        try:
            message_data = data['entry'][0]['changes'][0]['value']['messages'][0]
            phone_number = message_data['from'][-10:]
            incoming_text = message_data.get('text', {}).get('body', "").lower()
        except Exception as e:
            print("Webhook parsing error:", e)
            return "error", 200

        # 1. Try to match FAQ response
        faq_response = match_faq_response(incoming_text)

        if faq_response:
            send_whatsapp_message(phone_number, faq_response)
        else:
            # 2. If no FAQ match, fallback to Shopify order lookup
            shopify_response = get_order_details_by_phone(phone_number)
            print("Shopify response:", shopify_response)

            default_message = "We couldn't find any recent orders linked to this number. Please provide your order ID or contact support."

            try:
                orders = (
                    shopify_response["data"]["customers"]["nodes"][0]["orders"]["nodes"]
                    if shopify_response.get("data") and shopify_response["data"]["customers"]["nodes"]
                    else []
                )
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
    response = requests.post(url, json=payload, headers=headers)

    print("WhatsApp API Response:", response.status_code, response.text)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
