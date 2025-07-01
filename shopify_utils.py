import requests, os

SHOPIFY_API_TOKEN = os.getenv("SHOPIFY_API_TOKEN")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")

def normalize_phone_number(phone):
    phone = phone.replace("+91", "").replace(" ", "").strip()
    if len(phone) == 12 and phone.startswith("91"):
        return phone[2:]
    return phone[-10:]

def get_orders_by_phone(phone_number):
    query = {
        "query": f"""
        {{
            customers(query: "phone:*{phone_number}*") {{
                edges {{
                    node {{
                        id
                        firstName
                        lastName
                        phone
                        orders(first: 5, sortKey: CREATED_AT, reverse: true) {{
                            edges {{
                                node {{
                                    name
                                    createdAt
                                    fulfillmentStatus
                                    lineItems(first: 5) {{
                                        edges {{
                                            node {{
                                                title
                                                quantity
                                            }}
                                        }}
                                    }}
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
        "X-Shopify-Access-Token": SHOPIFY_API_TOKEN,
        "Content-Type": "application/json"
    }

    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/graphql.json"
    try:
        response = requests.post(url, json=query, headers=headers)
        data = response.json()

        customers = data["data"]["customers"]["edges"]
        if not customers:
            return None

        orders = customers[0]["node"]["orders"]["edges"]
        return orders

    except Exception as e:
        print("Shopify Error:", e)
        return None

def format_order_details(orders):
    message = "📦 Your recent orders:\n\n"
    for order in orders:
        node = order["node"]
        message += f"🧾 Order: {node['name']}\n📅 Date: {node['createdAt'][:10]}\n🚚 Status: {node['fulfillmentStatus'] or 'PENDING'}\n📦 Items:\n"
        for item in node["lineItems"]["edges"]:
            message += f" - {item['node']['title']} x{item['node']['quantity']}\n"
        message += "\n"
    return message



