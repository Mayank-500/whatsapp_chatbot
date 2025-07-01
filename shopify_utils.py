import requests, os
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_API_TOKEN = os.getenv("SHOPIFY_API_TOKEN")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")

def normalize_phone_number(raw_phone):
    if not raw_phone:
        return ""
    phone = raw_phone.strip()
    if phone.startswith("0"):
        phone = phone[1:]
    if not phone.startswith("+91"):
        phone = "+91" + phone
    return phone

def get_orders_by_phone(phone):
    normalized_phone = normalize_phone_number(phone)
    query = f'''
    {{
      customers(first: 1, query: "phone:*{normalized_phone}") {{
        edges {{
          node {{
            firstName
            phone
            orders(first: 5, sortKey: PROCESSED_AT, reverse: true) {{
              edges {{
                node {{
                  name
                  financialStatus
                  fulfillmentStatus
                  processedAt
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_API_TOKEN,
        "Content-Type": "application/json"
    }
    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/graphql.json"
    response = requests.post(url, headers=headers, json={"query": query})
    try:
        data = response.json()
        customer_edges = data["data"]["customers"]["edges"]
        if customer_edges:
            return customer_edges[0]["node"]["orders"]["edges"]
    except Exception as e:
        print("Shopify error:", e)
    return []

def format_order_details(order_edges):
    if not order_edges:
        return "No recent orders found."
    latest_order = order_edges[0]["node"]
    response = f"🧾 *Order Details:*\n"
    response += f"📦 Order ID: {latest_order['name']}\n"
    response += f"💰 Payment: {latest_order['financialStatus']}\n"
    response += f"🚚 Status: {latest_order['fulfillmentStatus']}\n"
    response += f"📅 Ordered on: {latest_order['processedAt'][:10]}\n"
    return response


