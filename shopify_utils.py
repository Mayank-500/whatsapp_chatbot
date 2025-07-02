import os
import requests

# ✅ Make sure this is the full HTTPS URL
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
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
        return response.json()
    except Exception as e:
        print(f"❌ Shopify API error: {e}")
        return {"error": "Request failed"}


def format_order_summary(order):
    name = order.get("name")
    status = order.get("displayFulfillmentStatus")
    items = order.get("lineItems", {}).get("nodes", [])

    item_lines = "\n".join([f"  - {item['title']} (x{item['quantity']})" for item in items])
    return f"🧾 Order: {name}\n📦 Status: {status}\n🛍️ Items:\n{item_lines}"
