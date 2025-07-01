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
            customers(query: "phone:+91{phone_number}") {{
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
        "X-Shopify-Access-Token": SHOPIFY_API_TOKEN,
        "Content-Type": "application/json"
    }

    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/graphql.json"
    try:
        print("📞 Shopify phone used:", phone_number)
        print("📤 GraphQL query sent:\n", query["query"])

        response = requests.post(url, json=query, headers=headers)
        print("📦 Shopify response:\n", response.text)

        data = response.json()
        customers = data["data"]["customers"]["nodes"]
        if not customers:
            print("⚠️ No customers found")
            return None

        orders = customers[0]["orders"]["nodes"]
        if not orders:
            print("⚠️ No orders found for this customer")
            return None

        return orders

    except Exception as e:
        print("❌ Shopify Error:", e)
        return None

def format_order_details(orders):
    message = "📦 Your recent orders:\n\n"
    for order in orders:
        message += f"🧾 Order: {order['name']}\n"
        message += f"📅 Date: {order['createdAt'][:10]}\n"
        message += f"🚚 Status: {order['displayFulfillmentStatus'] or 'PENDING'}\n📦 Items:\n"
        for item in order["lineItems"]["nodes"]:
            message += f" - {item['title']} x{item['quantity']}\n"
        message += "\n"
    return message
