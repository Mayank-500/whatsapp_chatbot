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
        user_id = message['from']
        user_text = message['text']['body'].strip().lower()

        # Step 1: Check for predefined FAQ
        reply = check_faq(user_text)

        # Step 2: Handle special Shopify flow (e.g. order inquiry)
        if not reply and "order" in user_text:
            orders = get_orders_by_phone(user_id)
            if orders:
                reply = format_order_details(orders)
            else:
                reply = "Sorry, we couldn't find any recent orders linked to this number. Please provide your order ID or try again later."

        # Step 3: Use GPT to infer intent if not found
        if not reply:
            intent = get_intent_from_gpt(user_text)
            reply = route_intent(intent)

        send_whatsapp_message(user_id, reply)

    except Exception as e:
        print("Error:", e)

    return "OK", 200

def check_faq(message):
    for category, entry in faq.items():
        if isinstance(entry, dict) and "keywords" in entry:
            for keyword in entry["keywords"]:
                if keyword in message:
                    return entry["response"]
    return None

def get_intent_from_gpt(message):
    prompt = f"What is the user's intent for this message: \"{message}\"? Return one of the following categories: order, product, consultation, complaint, greeting, unknown."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"].strip().lower()
    except Exception as e:
        print("OpenAI error:", e)
        return "unknown"

def route_intent(intent):
    if intent == "order":
        return "Please share your phone number or order ID so we can check your order details."
    elif intent == "product":
        return "Check out our product collection: https://tacx.in/shop"
    elif intent == "consultation":
        return "Book a free consultation here: https://tacx.in/consult"
    elif intent == "complaint":
        return "Sorry for the inconvenience. Raise your concern here: https://tacx.in/support"
    elif intent == "greeting":
        return "Namaste 👋 How can I assist you today?"
    else:
        return "I'm not sure I understand. You can ask about products, orders, or consultations."

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
