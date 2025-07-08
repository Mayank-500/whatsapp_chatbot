import os
import requests
from dotenv import load_dotenv

load_dotenv()
SHOPIFY_API_URL = os.getenv("SHOPIFY_API_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

QUERY_TEMPLATE = """
query {
  customers(first: 10, query: "phone:%s") {
    nodes {
      firstName
      orders(first: 1, reverse: true) {
        nodes {
          name
          displayFulfillmentStatus
        }
      }
    }
  }
}
"""

def fetch_order_status_by_phone(phone):
    try:
        query = QUERY_TEMPLATE % phone
        response = requests.post(
            SHOPIFY_API_URL,
            headers=HEADERS,
            json={"query": query}
        )
        data = response.json()
        customers = data.get("data", {}).get("customers", {}).get("nodes", [])
        if not customers:
            return "No customer found with this phone number."

        orders = customers[0].get("orders", {}).get("nodes", [])
        if not orders:
            return "No recent orders found for this number."

        latest = orders[0]
        return f"Order {latest['name']} is currently: {latest['displayFulfillmentStatus']}."
    except Exception as e:
        print("Shopify error:", e)
        return "Could not fetch order. Try again later."

