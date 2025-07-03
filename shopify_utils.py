import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment config
SHOPIFY_API_URL = os.getenv("SHOPIFY_API_URL")  # e.g., https://yourstore.myshopify.com/admin/api/2023-04/graphql.json
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

# Headers
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

# GraphQL query template
QUERY_TEMPLATE = """
query GetCustomers {
  customers(first: 10, query: "phone:%s") {
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
    Fetches the most recent Shopify order status by phone number.
    Returns a string message.
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

        # Extract customer data
        customers = data.get("data", {}).get("customers", {}).get("nodes", [])

        if not customers:
            return f"❌ No customer found with phone number: {phone_number}"

        customer = customers[0]
        orders = customer.get("orders", {}).get("nodes", [])

        if not orders:
            return f"📭 No orders found for {customer.get('firstName', 'this customer')}."

        # Get most recent order
        latest_order = orders[0]
        order_name = latest_order.get("name")
        status = latest_order.get("displayFulfillmentStatus")

        return f"📦 Order *{order_name}* is currently: *{status}*."

    except Exception as e:
        print("❌ Shopify Exception:", e)
        return "⚠️ Internal error while fetching order. Please try again."
