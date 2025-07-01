import requests
import os

SHOPIFY_DOMAIN = "the-ayurveda-co.myshopify.com"
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")  # Set this in .env or Render Dashboard

def get_order_by_phone(phone):
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    url = f"https://{SHOPIFY_DOMAIN}/admin/api/2023-10/orders.json?status=any&fields=name,phone,line_items,fulfillment_status"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        orders = response.json().get("orders", [])
        for order in orders:
            order_phone = order.get("phone", "")
            if order_phone and phone[-10:] in order_phone[-10:]:
                return order
    return None
