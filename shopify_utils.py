import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Shopify environment variables
SHOPIFY_API_URL = os.getenv("SHOPIFY_API_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

QUERY_TEMPLATE = """
query GetCustomers {
  customers(first: 5, query: "phone:%s") {
    nodes {
      firstName
      lastName
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
    """
    Fetch the latest Shopify order for a given phone number.
    """
    query = QUERY_TEMPLATE % phone_number

    try:
        response = requests.post(
            SHOPIFY_API_URL,
            headers=HEADERS,
            json={"query": query}
        )

        if response.status_code != 200:
            print("⚠️ Shopify API error:", response.text)
            return "❌ Failed to fetch order details. Please try again later."

        data = response.json()
        customers = data.get("data", {}).get("customers", {}).get("nodes", [])

        if not customers:
            return f"❌ No customer found with phone number: {phone_number}"

        customer = customers[0]
        orders = customer.get("orders", {}).get("nodes", [])

        if not orders:
            return f"📭 No orders found for {customer.get('firstName', 'this customer')}."

        latest_order = orders[0]
        order_name = latest_order.get("name")
        status = latest_order.get("displayFulfillmentStatus")

        return f"📦 Order *{order_name}* is currently: *{status}*."

    except Exception as e:
        print("❌ Shopify Exception:", e)
        return "⚠️ Internal error while fetching order. Please try again."

