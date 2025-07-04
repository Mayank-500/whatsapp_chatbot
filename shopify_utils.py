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
query GetCustomers {
  customers(first: 10, query: "phone:%s") {
    nodes {
      firstName
      phone
      orders(first: 5, reverse: true) {
        nodes {
          name
          displayFulfillmentStatus
        }
      }
    }
  }
}
"""

def fetch_order_status_by_phone(phone_number):
    query = QUERY_TEMPLATE % phone_number

    try:
        response = requests.post(SHOPIFY_API_URL, headers=HEADERS, json={"query": query})
        if response.status_code != 200:
            return "Failed to fetch order details. Please try again later."

        data = response.json()
        customers = data.get("data", {}).get("customers", {}).get("nodes", [])

        if not customers:
            return f"No customer found with phone: {phone_number}"

        customer = customers[0]
        orders = customer.get("orders", {}).get("nodes", [])
        if not orders:
            return "No orders found for this customer."

        latest_order = orders[0]
        return f"Order {latest_order.get('name')} is currently: {latest_order.get('displayFulfillmentStatus')}."

    except Exception as e:
        print("Shopify Error:", e)
        return "Internal error while fetching order. Please try again."
