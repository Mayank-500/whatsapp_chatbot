import json

# Load FAQ
try:
    with open("faq.json") as f:
        FAQ_DATA = json.load(f)
        print("✅ FAQ loaded with categories:", list(FAQ_DATA.keys()))
except Exception as e:
    FAQ_DATA = {}
    print("❌ Failed to load faq.json:", e)

def match_faq_response(message):
    message = message.lower()
    print("🔍 Matching message:", message)
    for category, info in FAQ_DATA.items():
        for keyword in info.get("keywords", []):
            if keyword in message:
                print(f"✅ Matched keyword '{keyword}' in category '{category}'")
                return info["response"]
    print("❌ No keyword matched.")
    return None
