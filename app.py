from flask import Flask, request
import requests
import json
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

# Set OpenAI key
openai.api_key = OPENAI_API_KEY

# Load FAQ JSON
FAQ_FILE = "faq.json"
faq = {}
if os.path.exists(FAQ_FILE):
    with open(FAQ_FILE, "r") as f:
        faq = json.load(f)

# -------------------- Webhook Verification --------------------
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# -------------------- Webhook for WhatsApp Messages --------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_id = message['from']
        user_text = message['text']['body'].lower()

        # Step 1: Try to find a structured reply from faq.json
        reply = check_faq(user_text)

        # Step 2: If not found, use GPT to classify intent and route
        if reply is None:
            intent = get_intent_from_gpt(user_text)
            reply = route_intent(intent)

            # Optionally store unknown for future training
            faq[user_text] = reply
            with open(FAQ_FILE, "w") as f:
                json.dump(faq, f, indent=2)

        send_whatsapp_message(user_id, reply)

    except Exception as e:
        print("Error:", e)

    return "OK", 200

# -------------------- Helper Functions --------------------

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
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        intent = response.choices[0].message["content"].strip().lower()
        print("GPT-detected intent:", intent)
        return intent
    except Exception as e:
        print("OpenAI error:", e)
        return "unknown"

def route_intent(intent):
    if intent == "order":
        return "You can track your order here: https://tacx.in/track-order"
    elif intent == "product":
        return "Please visit our product page: https://tacx.in/shop"
    elif intent == "consultation":
        return "You can book a free consultation here: https://tacx.in/consult"
    elif intent == "complaint":
        return "We are sorry for the inconvenience. Please report your issue here: https://tacx.in/support"
    elif intent == "greeting":
        return "Hello. How can I assist you today?"
    else:
        return "I'm not sure I understand. Please ask about order, product, or consultation."

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

# -------------------- Start Flask App --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5057))  # Use Render's dynamic port if set
    app.run(host="0.0.0.0", port=port)


