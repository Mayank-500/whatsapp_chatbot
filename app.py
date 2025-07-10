from flask import Flask, request
import requests, json, os, re
from dotenv import load_dotenv
from shopify_utils import fetch_order_status_by_phone
from gemini_handler import smart_gemini_reply

load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

FAQ_FILE = "faq.json"
faq = {}
if os.path.exists(FAQ_FILE):
    with open(FAQ_FILE, "r") as f:
        faq = json.load(f)

# Store session-like state in memory (basic for now)
user_sessions = {}

ABUSIVE_KEYWORDS = set([
    "fuck", "bitch", "bastard", "mc", "bc", "madarchod", "behenchod", "chutiya",
    "chut", "gaand", "gandu", "haraami", "kutte", "kutti", "chinki", "randi",
    "lavda", "launda", "lund", "chod", "chodna", "sex", "nude", "xxx", "horny",
    "hijra", "homo", "loda", "bhosdi", "nangi", "choddo", "lund", "bhadwa",
    "suar", "kutta", "gaandfat", "gaandmasti", "sali", "saala", "chudai", "sambhog",
    "intercourse", "fuckoff", "dick", "pussy", "asshole", "arse", "muth", "tharki",
    "gand", "porn", "masturbate", "masturbation", "boobs", "ling", "yoni", "lingam",
    "condom", "erection", "fetish", "blowjob", "doggy", "69", "strip", "sambhog",
    "bosdike", "aand", "suar ki aulad", "tatti", "bakchod", "chodu", "gaand mara", "maal", "hot girl"
])

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
            print("⚠️ Non-text message received")
            return "OK", 200

        user_text = message['text']['body'].strip().lower()
        print(f"📩 Incoming: {user_text}")

        # Abusive content check
        if any(abuse in user_text for abuse in ABUSIVE_KEYWORDS):
            reply = "⚠️ Let's keep things respectful. If you're feeling stressed, Ashwagandha is great for calming the mind. 🌿"
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        # Phone number check
        phone = extract_phone_number(user_text)
        if phone:
            reply = fetch_order_status_by_phone(phone)
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        # FAQ match
        reply = check_faq(user_text)
        if reply:
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        # Session Quiz
        if user_id not in user_sessions:
            user_sessions[user_id] = {"stage": None}

        session = user_sessions[user_id]

        if user_text in ["start quiz", "start", "quiz", "1"]:
            session["stage"] = "quiz_started"
            reply = ("Let's begin your Ayurvedic Discovery Quiz! 🌿\n\n"
                     "What's your primary concern?\n"
                     "1. Skin Issues\n"
                     "2. Hair Fall\n"
                     "3. Digestion\n"
                     "4. Immunity\n(Reply with the number)")
            send_whatsapp_message(user_id, reply)
            return "OK", 200

        if session.get("stage") == "quiz_started":
            if user_text in ["1", "2", "3", "4"]:
                result = {
                    "1": "🌿 *Skin Care Tip*: Try our Kumkumadi Face Wash for bright, glowing skin!",
                    "2": "🧠 *Hair Fall Tip*: Our Dashmool Hair Oil strengthens roots and reduces breakage.",
                    "3": "🔥 *Digestion Boost*: Triphala Juice supports gentle detox and digestive balance.",
                    "4": "💪 *Immunity Support*: Amla Juice & Ashwagandha Tablets are great daily picks."
                }
                send_whatsapp_message(user_id, result[user_text])
                session["stage"] = None
                return "OK", 200

        # Gemini fallback
        gemini_reply = smart_gemini_reply(user_text)
        send_whatsapp_message(user_id, gemini_reply)

    except Exception as e:
        print("❌ Webhook error:", e)

    return "OK", 200

def extract_phone_number(msg):
    match = re.search(r"\b\d{10}\b", msg)
    if match:
        return "+91" + match.group()
    return None

def check_faq(msg):
    for key, entry in faq.items():
        if isinstance(entry, dict) and "keywords" in entry:
            for keyword in entry["keywords"]:
                if keyword.lower() in msg:
                    return entry.get("response")
    return None

def send_whatsapp_message(to, message):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    r = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print("✅ Sent:", r.status_code)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
