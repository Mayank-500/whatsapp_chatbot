import os
import requests

SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")  # Should be: https://the-ayurveda-co.myshopify.com/admin/api/2023-10/graphql.json
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

def get_order_details_by_phone(phone_number):
    """
    Fetch latest Shopify orders by phone number using GraphQL.
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
        return {"error": str(e)}

def format_order_summary(order):
    """
    Format order details for WhatsApp message.
    """
    name = order.get("name")
    status = order.get("displayFulfillmentStatus")
    items = order.get("lineItems", {}).get("nodes", [])

    item_lines = "\n".join([f"  - {item['title']} (x{item['quantity']})" for item in items])
    return f"🧾 Order: {name}\n📦 Status: {status}\n🛍️ Items:\n{item_lines}"
