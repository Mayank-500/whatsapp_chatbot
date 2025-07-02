import os
import requests

SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

def get_order_details_by_phone(phone_number):
    # GraphQL query to find customers by phone number
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

    response = requests.post(SHOPIFY_STORE_URL, json=query, headers=headers)
    try:
        return response.json()
    except Exception as e:
        print("Error parsing Shopify response:", e)
        return {"error": "Invalid JSON response"}

def format_order_summary(order):
    name = order.get("name")
    status = order.get("displayFulfillmentStatus")
    items = order.get("lineItems", {}).get("nodes", [])

    item_lines = "\n".join([f"- {item['title']} (x{item['quantity']})" for item in items])
    return f"Order: {name}\nStatus: {status}\nItems:\n{item_lines}"
