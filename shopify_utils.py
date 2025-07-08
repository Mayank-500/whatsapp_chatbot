import requests
import os
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")  # e.g., tacx.myshopify.com
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")  # Admin API access token

def fetch_order_status_by_phone(phone_number):
    try:
        url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2023-07/orders.json?status=any&fields=id,name,phone,financial_status,fulfillment_status"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        orders = response.json().get("orders", [])

        matched_orders = [order for order in orders if order.get("phone", "").endswith(phone_number)]

        if not matched_orders:
            return "⚠️ No orders found for this phone number. Please check and try again."

        latest_order = matched_orders[0]  # Optional: Use latest order if multiple match
        order_id = latest_order.get("name", "Unknown")
        fulfillment_status = latest_order.get("fulfillment_status", "Unfulfilled").upper()

        return f"📦 Order {order_id} is currently: {fulfillment_status}."

    except requests.exceptions.RequestException as e:
        print(f"[Shopify API Error] {str(e)}")
        return "❌ Could not connect to Shopify. Please try again later."
    except Exception as e:
        print(f"[fetch_order_status_by_phone Error] {str(e)}")
        return "⚠️ Unexpected error while fetching order status."
