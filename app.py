from flask import Flask, request
import requests
import json
import os
from dotenv import load_dotenv
import openai

from shopify_utils import fetch_order_status_by_phone

# Load environment variables
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Health product URLs (example)
product_urls = {
    "ashwagandha": "https://tacx.in/products/ashwagandha-capsules",
    "triphala": "https://tacx.in/products/triphala",
}

@app.route('/')
def index():
    return "TACX WhatsApp Bot is running!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Invalid verification token", 403

    elif request.method == "POST":
        try:
            data = request.get_json()
            print(f"[WEBHOOK] Incoming:\n{json.dumps(data, indent=2)}")

            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    if messages:
                        for message in messages:
                            phone_number = value["metadata"]["display_phone_number"]
                            user_number = message["from"]
                            msg_text = message["text"]["body"].strip().lower()

                            if "order" in msg_text and any(char.isdigit() for char in msg_text):
                                # Example: "check order for 9414562857"
                                digits = ''.join(filter(str.isdigit, msg_text))
                                order_status = fetch_order_status_by_phone(digits)
                                send_whatsapp_message(user_number, order_status)

                            elif any(kw in msg_text for kw in ["ashwagandha", "triphala", "giloy"]):
                                for keyword in product_urls:
                                    if keyword in msg_text:
                                        url = product_urls[keyword]
                                        ai_response = process_openai_query(msg_text)
                                        final_reply = f"{ai_response}\n\n🌿 Recommended for you: {url}"
                                        send_whatsapp_message(user_number, final_reply)
                                        break

                            elif msg_text in ["hi", "hello", "namaste"]:
                                send_whatsapp_message(user_number, 
                                    "Namaste. Welcome to TACX - The Ayurveda Co. How may I assist you today?\n"
                                    "1. Explore Products\n2. Book Consultation\n3. Track Order\n4. Ask a Health Question"
                                )
                            else:
                                send_whatsapp_message(user_number, 
                                    "🧠 Our expert will get back to you soon.\n"
                                    "🌐 Visit: https://tacx.in"
                                )

        except Exception as e:
            print(f"[ERROR in webhook] {str(e)}")
            return "Internal Server Error", 500

        return "ok", 200

def process_openai_query(query):
    try:
        print(f"[OpenAI] Query: {query}")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful Ayurveda expert."},
                {"role": "user", "content": query}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"[OpenAI ERROR] {str(e)}")
        return "🧠 Our expert will get back to you soon."

def send_whatsapp_message(to, message):
    try:
        url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        response = requests.post(url, headers=headers, json=payload)
        print(f"[WHATSAPP RESPONSE] {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERROR sending message] {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
