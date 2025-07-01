from flask import Flask, request
import requests, json, os
from dotenv import load_dotenv
import openai
from shopify_utils import get_orders_by_phone, format_order_details, normalize_phone_number

# Load environment variables
load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

FAQ_FILE = "faq.json"
faq = {}
if os.path.exists(FAQ_FILE):
    with open(FAQ_FILE, "r") as f:
        faq = json.load(f)

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_id = message['from']  # WhatsApp phone number
        user_text = message['text']['body'].strip().lower()

        reply = check_faq(user_text)

        # Order check flow
        if not reply and "order" in user_text:
            sanitized_number = normalize_phone_number(user_id)
            orders = get_orders_by_phone(sanitized_number)
            if orders:
                reply = format_order_details(orders)
            else:
                reply = "We couldn’t find recent orders linked to this number. You can reply with your order ID to check manually."

        # GPT fallback
        if not reply:
            intent = get_intent_from_gpt(user_text)
            reply = route_intent(intent)

        send_whatsapp_message(user_id, reply)

    except Exception as e:
        print("Webhook Error:", e)

    return "OK", 200

def check_faq(message):
    for category, entry in faq.items():
        if isinstance(entry, dict) and "keywords" in entry:
            for keyword in entry["keywords"]:
                if keyword in message:
                    return entry["response"]
    return None

def get_intent_from_gpt(message):
    prompt = f"What is the user's intent for this message: \"{message}\"? Choose one: order, product, consultation, complaint, greeting, unknown."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"].strip().lower()
    except Exception as e:
        print("OpenAI Error:", e)
        return "unknown"

def route_intent(intent):
    if intent == "order":
        return "Please share your phone number or order ID so we can check your order details."
    elif intent == "product":
        return "Check out our product collection: https://tacx.in/shop"
    elif intent == "consultation":
        return "Book a free consultation here: https://tacx.in/consult"
    elif intent == "complaint":
        return "Sorry for the trouble. You can raise a support request here: https://tacx.in/support"
    elif intent == "greeting":
        return "Namaste! 🌿 How can I assist you today?"
    else:
        return "I didn’t get that. You can ask about your orders, products, or consultations."

def send_whatsapp_message(to, message):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    r = requests.post(f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages", headers=headers, json=payload)
    print("Sent:", r.status_code, r.text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5057))
    app.run(host="0.0.0.0", port=port)
