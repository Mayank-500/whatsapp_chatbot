import os
import requests

# ✅ Corrected with "https://" schema and correct endpoint
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL", "https://the-ayurveda-co.myshopify.com/admin/api/2025-04/graphql.json")
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

    response = requests.post(SHOPIFY_STORE_URL, json=query, headers=headers)

    try:
        return response.json()
    except Exception as e:
        print(f"❌ Error parsing Shopify response: {e}")
        return {"error": "Invalid JSON response"}

def format_order_summary(order):
    """
    Return a formatted string of a Shopify order for WhatsApp message.
    """
    name = order.get("name")
    status = order.get("displayFulfillmentStatus")
    items = order.get("lineItems", {}).get("nodes", [])

    item_lines = "\n".join([f"  - {item['title']} (x{item['quantity']})" for item in items])
    return f"🧾 Order: {name}\n📦 Status: {status}\n🛍️ Items:\n{item_lines}"

# Optional REST fallback (currently not used)
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
