import os
import requests

# ✅ Corrected: Must include https:// schema
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")  # Example: "https://the-ayurveda-co.myshopify.com/admin/api/2025-04/graphql.json"
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

def get_order_details_by_phone(phone_number):
    """
    Fetch latest Shopify orders by phone number (GraphQL).
    """
    query = {
        "query": f"""
        {{
            customers(first: 10, query: "phone:+91{phone_number}") {{
                nodes {{
                    orders(first: 5, sortKey: CREATED_AT, reverse: true) {{
                        nodes {{
                            name
                            createdAt
                            displayFulfillmentStatus
                            lineItems(first: 5) {{
                                nodes {{
                                    title
                                    quantity
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
    }

    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }

    try:
        response = requests.post(SHOPIFY_STORE_URL, json=query, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Shopify API Error: {e}")
        return {"error": "Shopify request failed"}

def format_order_summary(order):
    """
    Format a single order for WhatsApp.
    """
    name = order.get("name")
    status = order.get("displayFulfillmentStatus")
    items = order.get("lineItems", {}).get("nodes", [])

    item_lines = "\n".join([f"  - {item['title']} (x{item['quantity']})" for item in items])
    return f"🧾 Order: {name}\n📦 Status: {status}\n🛍️ Items:\n{item_lines}"

# Optional REST fallback
def get_order_by_id_rest(order_id):
    url = f"https://the-ayurveda-co.myshopify.com/admin/api/2024-04/orders/{order_id}.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ REST API Error for Order ID {order_id}: {e}")
        return None
