from flask import Flask, request
import os
from dotenv import load_dotenv

from gemini_handler import smart_gemini_reply
from shopify_utils import fetch_order_status_by_phone  

load_dotenv()
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Gemini AI WhatsApp Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        user_message = data["message"]
        reply = smart_gemini_reply(user_message)
        return {"reply": reply}, 200
    return {"error": "Invalid payload"}, 400

if __name__ == "__main__":
    app.run(debug=True)
