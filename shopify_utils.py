import os
import requests

# Load credentials from environment variables
SHOPIFY_API_TOKEN = os.getenv("SHOPIFY_API_TOKEN")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")  # e.g., tacx-store.myshopify.com

SHOPIFY_GRAPHQL_URL = f"https://{SHOPIFY_STORE_URL}/admin/api/2024-04/graphql.json"
HEADERS = {
    "X-Shopify-Access-Token": SHOPIFY_API_TOKEN,
    "Content-Type": "application/json"
}

def get_latest_order_by_phone(phone_number):
    """
    Returns the most recent order placed using the given phone number.
    """
    query = """
    {
      orders(first: 5, query: "phone:{phone_number}", sortKey: CREATED_AT, reverse: true) {
        edges {
          node {
            name
            id
            createdAt
            financialStatus
            fulfillmentStatus
            totalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            lineItems(first: 5) {
              edges {
                node {
                  title
                  quantity
                }
              }
            }
            shippingAddress {
              name
              address1
              city
              phone
            }
          }
        }
      }
    }
    """.replace("{phone_number}", phone_number)

    response = requests.post(SHOPIFY_GRAPHQL_URL, headers=HEADERS, json={"query": query})
    data = response.json()

    try:
        order = data["data"]["orders"]["edges"][0]["node"]
        items = "\n".join(
            f"- {edge['node']['title']} (Qty: {edge['node']['quantity']})"
            for edge in order["lineItems"]["edges"]
        )
        total = order["totalPriceSet"]["shopMoney"]["amount"]
        currency = order["totalPriceSet"]["shopMoney"]["currencyCode"]
        reply = f"""🧾 *Latest Order Details:*
Order ID: {order['name']}
Date: {order['createdAt']}
Status: {order['financialStatus']} / {order['fulfillmentStatus']}
Items:
{items}
Total: {total} {currency}
Shipping: {order['shippingAddress']['address1']}, {order['shippingAddress']['city']}
"""
        return reply
    except Exception as e:
        print("Error fetching latest order:", e)
        return "No recent orders found for this number."

def get_order_by_id(order_id):
    """
    Fetch details of an order by order ID (name).
    """
    query = f"""
    {{
      orders(first: 1, query: "name:{order_id}") {{
        edges {{
          node {{
            name
            createdAt
            financialStatus
            fulfillmentStatus
            totalPriceSet {{
              shopMoney {{
                amount
                currencyCode
              }}
            }}
            lineItems(first: 5) {{
              edges {{
                node {{
                  title
                  quantity
                }}
              }}
            }}
            shippingAddress {{
              name
              address1
              city
              phone
            }}
          }}
        }}
      }}
    }}
    """

    response = requests.post(SHOPIFY_GRAPHQL_URL, headers=HEADERS, json={"query": query})
    data = response.json()

    try:
        order = data["data"]["orders"]["edges"][0]["node"]
        items = "\n".join(
            f"- {edge['node']['title']} (Qty: {edge['node']['quantity']})"
            for edge in order["lineItems"]["edges"]
        )
        total = order["totalPriceSet"]["shopMoney"]["amount"]
        currency = order["totalPriceSet"]["shopMoney"]["currencyCode"]
        reply = f"""🧾 *Order {order['name']} Details:*
Date: {order['createdAt']}
Status: {order['financialStatus']} / {order['fulfillmentStatus']}
Items:
{items}
Total: {total} {currency}
Shipping: {order['shippingAddress']['address1']}, {order['shippingAddress']['city']}
"""
        return reply
    except Exception as e:
        print("Error fetching order by ID:", e)
        return "Sorry, we couldn't find your order. Please double-check the ID."
