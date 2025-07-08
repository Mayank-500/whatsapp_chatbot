from flask import Flask, request
import requests, json, os, re
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

# Load JSON files
try:
    faq = json.load(open("faq.json"))
    keyword_data = json.load(open("keyword.json"))
    core_key_map = json.load(open("core_key_to_product.json"))
    print("All JSON files loaded successfully.")
except Exception as e:
    print("Error loading JSON files:", e)
    faq, keyword_data, core_key_map = {}, {}, {}

# Webhook verification
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# Webhook listener
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_id = message['from']

        if 'text' not in message:
            return "OK", 200

        user_text = message['text']['body'].lower().strip()
        print("Incoming message:", user_text)

        # 0. Phone number check
        phone = extract_phone_number(user_text)
        if phone:
            print("Phone number detected:", phone)
            reply = fetch_order_status_by_phone(phone)
            return send_reply(user_id, reply)

        # 1. FAQ check
        reply = check_faq(user_text)
        if reply:
            print("FAQ matched.")
            return send_reply(user_id, reply)

        # 2. Keyword → GPT → Product
        core_key = match_keyword_to_core_key(user_text)
        print("Matched core_key:", core_key)
        if core_key:
            gpt_reply = get_openai_response(user_text)
            product_url = core_key_map.get(core_key, "")
            final_reply = f"🧠 {gpt_reply.strip()}\n\n🌿 Recommended for you: {product_url}"
            return send_reply(user_id, final_reply)

        # 3. Fallback
        print("No match found. Sending fallback message.")
        return send_reply(user_id, "I'm still learning. Please ask about our Ayurveda products, consultations or orders.")

    except Exception as e:
        print("Error in webhook:", e)
        return "Error", 500

# Helper: Extract phone number
def extract_phone_number(msg):
    match = re.search(r"\b\d{10}\b", msg)
    return "+91" + match.group() if match else None

# Helper: Send reply
def send_reply(user_id, text):
    payload = {
        "messaging_product": "whatsapp",
        "to": user_id,
        "text": {"body": text}
    }
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    r = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print("Reply sent. Status code:", r.status_code)
    return "OK", 200

# Helper: Check FAQ
def check_faq(msg):
    for category, entry in faq.items():
        for keyword in entry.get("keywords", []):
            if keyword.lower() in msg:
                return entry.get("response")
    return None

# ✅ FIXED: Helper: Match keyword to core key (case-insensitive, partial match)
def match_keyword_to_core_key(msg):
    msg = msg.lower()
    for core_key, keywords in keyword_data.items():
        for kw in keywords:
            if kw.lower() in msg:
                return core_key
    return None

# ✅ FIXED: Helper: Get OpenAI response (with better error handling)
def get_openai_response(msg):
    prompt = f"Act as an Ayurveda expert. Answer briefly:\n\nQ: {msg}\nA:"
    try:
        print("Sending prompt to OpenAI:", prompt)
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )
        reply = response.choices[0].message['content'].strip()
        print("OpenAI response:", reply)
        return reply
    except Exception as e:
        print("OpenAI error:", e)
        return "Our expert will get back to you soon."

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
