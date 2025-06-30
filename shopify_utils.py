import requests, os
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_API_TOKEN = os.getenv("SHOPIFY_API_TOKEN")

def get_order_details_by_phone(phone_number):
    query = """
    {
      orders(first: 3, query: "phone:*%s") {
        edges {
          node {
            name
            createdAt
            fulfillmentStatus
            financialStatus
            lineItems(first: 5) {
              edges {
                node {
                  name
                  quantity
                }
              }
            }
          }
        }
      }
    }
    """ % phone_number

    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2024-01/graphql.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_API_TOKEN,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json={"query": query}, headers=headers)
    try:
        data = response.json()["data"]["orders"]["edges"]
        if not data:
            return f"No orders found for number ending in {phone_number[-4:]}."

        messages = []
        for order in data:
            node = order["node"]
            items = "\n".join([f"- {li['node']['name']} x{li['node']['quantity']}" for li in node["lineItems"]["edges"]])
            msg = f"🧾 Order: {node['name']}\n📦 Status: {node['fulfillmentStatus']}\n💰 Payment: {node['financialStatus']}\n📅 Date: {node['createdAt'][:10]}\n🛍️ Items:\n{items}"
            messages.append(msg)

        return "\n\n".join(messages)
    except Exception as e:
        print("Shopify Error:", e)
        return "Sorry, we couldn’t fetch your order details right now."

