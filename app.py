from flask import Flask, request
import requests, json, os, re
from dotenv import load_dotenv
from collections import defaultdict

from shopify_utils import fetch_order_status_by_phone
from gemini_handler import smart_gemini_reply

load_dotenv()
app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

# In-memory sessions
user_sessions = defaultdict(dict)

# Load FAQ data
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

        if 'text' not in message:
            print("⚠️ Non-text message received:", message)
            return "OK", 200

        user_text = message['text']['body'].lower()
        print("📩 Received message:", user_text)

        phone = extract_phone_number(user_text)
        if phone:
            reply = fetch_order_status_by_phone(phone)
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        reply = check_faq(user_text)
        if reply:
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        session = user_sessions[user_id]
        if session.get("quiz_active"):
            reply = handle_quiz_flow(user_id, user_text)
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        reply = smart_gemini_reply(user_text)
        if "start quiz" in user_text:
            user_sessions[user_id]["quiz_active"] = True
            user_sessions[user_id]["quiz_step"] = 1
        send_whatsapp_message(user_id, reply)

    except Exception as e:
        print("❌ Webhook error:", e)

    return "OK", 200

def extract_phone_number(message):
    match = re.search(r"\b\d{10}\b", message)
    if match:
        return "+91" + match.group()
    return None

def check_faq(message):
    for category, entry in faq.items():
        if isinstance(entry, dict) and "keywords" in entry:
            for keyword in entry["keywords"]:
                if keyword.lower() in message:
                    return entry.get("response")
    return None

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
    print("✅ Message sent:", r.status_code, r.text)

def handle_quiz_flow(user_id, message):
    session = user_sessions[user_id]
    step = session.get("quiz_step", 1)

    if step == 1:
        session["quiz_step"] = 2
        return """Great! 🌿 Let’s begin. What’s your primary concern?

1. Skin Issues  
2. Hair Fall  
3. Digestion  
4. Immunity  
(Reply with the number)"""

    elif step == 2:
        if message.strip() == "1":
            session["quiz_step"] = 3
            return """✨ Got it – Skin!

What best describes your skin?

1. Dry or Dull  
2. Oily or Acne-prone  
3. Pigmented or Uneven  
(Reply with number)"""
        elif message.strip() == "2":
            session["quiz_active"] = False
            return """🌿 For Hair Fall:  
- *Dashmool Hair Oil*  
- *Shikakai Shampoo*

Explore → https://tacx.in/collections/hair-care"""
        elif message.strip() == "3":
            session["quiz_active"] = False
            return """🧘 For Digestion:  
- *Triphala Juice*  
- *Jeera Water Tablets*

Explore → https://tacx.in/collections/wellness"""
        elif message.strip() == "4":
            session["quiz_active"] = False
            return """💪 For Immunity:  
- *Amla Juice*  
- *Ashwagandha Tablets*

Explore → https://tacx.in/collections/immunity"""
        else:
            return "Please reply with 1, 2, 3, or 4."

    elif step == 3:
        session["quiz_active"] = False
        if message.strip() == "1":
            return """✨ For Dry/Dull Skin:  
- *Kumkumadi Face Oil*  
- *Eladi Body Butter*

Explore → https://tacx.in/collections/face-care"""
        elif message.strip() == "2":
            return """✨ For Oily/Acne-Prone Skin:  
- *Neem & Tea Tree Face Wash*  
- *Clarifying Anti-Acne Gel*

Explore → https://tacx.in/collections/face-care"""
        elif message.strip() == "3":
            return """✨ For Pigmented Skin:  
- *10% Kumkumadi Stick*  
- *Eladi & Triphala Face Polisher*

Explore → https://tacx.in/collections/face-care"""
        else:
            return "Please reply with 1, 2, or 3."

    return "Let’s restart the quiz? Type 'Start Quiz' to begin again."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

