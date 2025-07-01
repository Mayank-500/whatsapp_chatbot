import json
import re
from flask import Flask, request
from shopify_utils import get_order_by_phone

app = Flask(__name__)

# Load FAQ data
with open('faq.json', 'r') as f:
    faq_data = json.load(f)

def match_faq(message):
    for faq in faq_data:
        if any(keyword.lower() in message.lower() for keyword in faq['keywords']):
            return faq['response']
    return None

def normalize_phone_number(text):
    match = re.search(r'(\+91[\- ]?|0)?[6-9]\d{9}', text)
    if match:
        number = re.sub(r'\D', '', match.group())
        if not number.startswith('91'):
            number = '91' + number[-10:]
        return f'+{number}'
    return None

def get_order_response(phone_number):
    order = get_order_by_phone(phone_number)
    if order:
        return f"\ud83d\udce6 Here's your latest order:\n- Order ID: {order['name']}\n- Product: {order['line_items'][0]['name']}\n- Status: {order['fulfillment_status'] or 'Processing'}\nTrack: https://theayurvedaco.com/apps/tracktor/track"
    else:
        return "\u274c Sorry! No order found for this number.\nPlease check you used this number at checkout.\nManual track link: https://theayurvedaco.com/apps/tracktor/track"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == "nishu":
            return request.args.get("hub.challenge")
        return "Invalid verification token"

    data = request.get_json()
    try:
        message_text = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        phone_number = data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']

        response = match_faq(message_text)

        if not response:
            if re.search(r'check order for', message_text.lower()):
                num = normalize_phone_number(message_text)
                response = get_order_response(num) if num else "Please provide a valid phone number."
            elif re.search(r'(where is my order|order status)', message_text.lower()):
                normalized = normalize_phone_number(phone_number)
                response = get_order_response(normalized)
            else:
                response = "Namaste! Welcome to The Ayurveda Co. - your trusted wellness partner. How may we assist your healing journey today?"

        return json.dumps({"reply": response})

    except Exception as e:
        return json.dumps({"reply": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True, port=10000)
