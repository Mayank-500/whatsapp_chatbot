import os
import requests
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_API_TOKEN = os.getenv("SHOPIFY_API_TOKEN")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")

def normalize_phone_number(phone):
    phone = phone.strip()
    if phone.startswith("91") and len(phone) == 12:
        return "+" + phone
    elif phone.startswith("+91") and len(phone) == 13:
        return phone
    elif len(phone) == 10:
        return "+91" + phone
    else:
        return phone

def get_orders_by_phone(phone):
    try:
        headers = {
            "X-Shopify-Access-Token": SHOPIFY_API_TOKEN,
            "Content-Type": "application/json"
        }
        query = {
            "query": f"""
            {{
              customers(first: 1, query: "phone:{phone}") {{
                edges {{
                  node {{
                    id
                    orders(first: 3, sortKey: CREATED_AT, reverse: true) {{
                      edges {{
                        node {{
                          name
                          financialStatus
                          fulfillmentStatus
                          processedAt
                          totalPrice
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """
        }
        response = requests.post(f"https://{SHOPIFY_STORE_URL}/admin/api/2023-07/graphql.json", headers=headers, json=query)
        data = response.json()

        customer_edges = data.get("data", {}).get("customers", {}).get("edges", [])
        if not customer_edges:
            return None

        order_edges = customer_edges[0]["node"]["orders"]["edges"]
        return [edge["node"] for edge in order_edges]

    except Exception as e:
        print("Shopify Error:", e)
        return None

def format_order_details(orders):
    messages = []
    for order in orders:
        msg = f"🧾 *Order ID:* {order['name']}\n" \
              f"💰 *Total:* ₹{order['totalPrice']}\n" \
              f"📦 *Status:* {order['fulfillmentStatus'].capitalize() if order['fulfillmentStatus'] else 'Pending'}\n" \
              f"🕒 *Date:* {order['processedAt'][:10]}"
        messages.append(msg)
    return "\n\n".join(messages)
