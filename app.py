from flask import Flask, request
import requests, json, os, re
from dotenv import load_dotenv
import openai
from shopify_utils import fetch_order_status_by_phone

load_dotenv()
app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
openai.api_key = OPENAI_API_KEY

with open("faq.json") as f: faq = json.load(f)
with open("keywords.json") as f: keyword_data = json.load(f)
with open("core_key_to_product.json") as f: core_key_map = json.load(f)

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Unauthorized", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_id = msg['from']
        user_text = msg.get('text', {}).get('body', '').lower()

        phone = extract_phone_number(user_text)
        if phone:
            send_whatsapp_message(user_id, fetch_order_status_by_phone(phone))
            return "OK", 200

        faq_reply = check_faq(user_text)
        if faq_reply:
            send_whatsapp_message(user_id, faq_reply)
            return "OK", 200

        matched_core_key = check_keyword_trigger(user_text)
        if matched_core_key:
            expert_reply = get_answer_from_gpt(user_text)
            product = core_key_map.get(matched_core_key, "https://tacx.in/shop")
            full_reply = f"{expert_reply}\n\nRelated product: {product}"
            send_whatsapp_message(user_id, full_reply)
        else:
            send_whatsapp_message(user_id, "Sorry, I couldn't process that. Please ask about products, orders, or consultations.")

    except Exception as e:
        print("Webhook Error:", e)
    return "OK", 200

def extract_phone_number(msg): 
    match = re.search(r"\b\d{10}\b", msg)
    return "+91" + match.group() if match else None

def check_faq(msg):
    for _, entry in faq.items():
        for k in entry["keywords"]:
            if k in msg:
                return entry["response"]
    return None

def check_keyword_trigger(msg):
    for key, values in keyword_data.items():
        if any(v in msg for v in values):
            return key
    return None

def get_answer_from_gpt(msg):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": msg}]
        )
        return response.choices[0].message["content"].strip()
    except:
        return "I’m still learning. Please ask about our Ayurvedic offerings."

def send_whatsapp_message(to, msg):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "text": {"body": msg}}
    requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
