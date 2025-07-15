import requests
import os
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")  # e.g., 'https://yourstore.myshopify.com'
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

def fetch_order_status_by_phone(phone_number):
    """
    Fetch order status using Shopify Admin API by phone number.
    Assumes `phone_number` is in international format (e.g., +91XXXXXXXXXX or 91XXXXXXXXXX).
    """
    try:
        url = f"{SHOPIFY_STORE_URL}/admin/api/2023-07/orders.json?status=any"
        headers = {
            "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("❌ Shopify API error:", response.status_code, response.text)
            return None

        orders = response.json().get("orders", [])
        for order in orders:
            customer = order.get("customer", {})
            if customer:
                customer_phone = str(customer.get("phone", "")).replace("+", "").replace(" ", "")
                if phone_number[-10:] in customer_phone[-10:]:
                    return f"📦 Order #{order['name']} is currently *{order['fulfillment_status'] or 'unfulfilled'}*."

        return None  # No matching order found

    except Exception as e:
        print("❌ Shopify fetch error:", e)
        return None
