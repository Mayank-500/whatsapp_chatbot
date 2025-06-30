from flask import Flask, request
import requests, json, os, re
from dotenv import load_dotenv
import openai
from shopify_utils import get_order_details_by_phone

# Load environment variables
load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI Key
openai.api_key = OPENAI_API_KEY

# WhatsApp API URL
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

# Load FAQ file
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
        user_text = message['text']['body'].lower()

        # Manual phone number input handling
        phone_match = re.findall(r'\b\d{10,13}\b', user_text)
        if phone_match:
            phone_to_check = phone_match[0][-10:]
            reply = get_order_details_by_phone(phone_to_check)
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        # First try structured FAQ
        reply = check_faq(user_text)

        # GPT fallback
        if reply is None:
            intent = get_intent_from_gpt(user_text)
            if intent == "order":
                reply = get_order_details_by_phone(user_id[-10:])  # last 10 digits
            else:
                reply = route_intent(intent)
            faq[user_text] = reply
            with open(FAQ_FILE, "w") as f:
                json.dump(faq, f, indent=2)

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
    prompt = f"What is the user's intent for this message: \"{message}\"? Return one of: order, product, consultation, complaint, greeting, unknown."
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
    responses = {
        "order": "Let me check your order status using your phone number...",
        "product": "Please explore our natural health products at https://tacx.in/shop",
        "consultation": "You can book a free wellness consultation here: https://tacx.in/consult",
        "complaint": "We’re sorry for the issue. Please raise it here: https://tacx.in/support",
        "greeting": "Namaste 🙏 How can we help you on your wellness journey today?",
        "unknown": "I’m not sure I understood. Try asking about your order, products, or a consultation."
    }
    return responses.get(intent, responses["unknown"])

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
    r = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print("Sent:", r.status_code, r.text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
