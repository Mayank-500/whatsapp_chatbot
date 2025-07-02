import json

# Load FAQ responses from JSON
with open("faq.json") as f:
    FAQ_DATA = json.load(f)

def match_faq_response(message):
    message = message.lower()
    for category in FAQ_DATA.values():
        for keyword in category["keywords"]:
            if keyword in message:
                return category["response"]
    return None
