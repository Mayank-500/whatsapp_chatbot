from flask import Flask, request
import requests
import json
import os
import re
from dotenv import load_dotenv
import openai

from shopify_utils import fetch_order_status_by_phone

# Load environment variables
load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

openai.api_key = OPENAI_API_KEY

# Load static files
with open("faq.json", "r") as f:
    faq = json.load(f)

with open("keyword.json", "r") as f:
    keyword_data = json.load(f)

with open("core_key_to_product.json", "r") as f:
    core_product_map = json.load(f)

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

        if 'text' not in message:
            return "OK", 200

        user_text = message['text']['body'].lower()

        # Phone number detection for order check
        phone = extract_phone_number(user_text)
        if phone:
            reply = fetch_order_status_by_phone(phone)
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        # Static FAQ match
        faq_reply = check_faq(user_text)
        if faq_reply:
            send_whatsapp_message(user_id, faq_reply)
            return "OK", 200

        # Keyword match → GPT reply + product
        matched_core_key = match_keyword(user_text)
        if matched_core_key:
            gpt_reply = get_openai_answer(user_text)
            product_suggestion = core_product_map.get(matched_core_key)
            full_reply = gpt_reply
            if product_suggestion:
                full_reply += f"\n\nRecommended for you: {product_suggestion}"
            send_whatsapp_message(user_id, full_reply)
            return "OK", 200

        # Fallback
        send_whatsapp_message(user_id, "Sorry, I couldn't process that. Please ask again.")
    except Exception as e:
        print("Webhook error:", e)
    return "OK", 200

def extract_phone_number(message):
    match = re.search(r"\b\d{10}\b", message)
    return "+91" + match.group() if match else None

def check_faq(message):
    for category, entry in faq.items():
        for keyword in entry["keywords"]:
            if keyword.lower() in message:
                return entry["response"]
    return None

def match_keyword(message):
    for core_key, keywords in keyword_data.items():
        for keyword in keywords:
            if keyword.lower() in message:
                return core_key
    return None

def get_openai_answer(message):
    try:
        prompt = f"You're an Ayurvedic expert from The Ayurveda Co. Answer this customer query:\n{message}"
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.6
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print("OpenAI Error:", e)
        return "Our expert will get back to you soon."

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
    requests.post(WHATSAPP_API_URL, headers=headers, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

