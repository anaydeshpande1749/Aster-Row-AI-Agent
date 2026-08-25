import json
import re

from app.config import ORDERS_FILE


def load_orders():
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["orders"], data["snapshot_at"]


def normalize_order_id(order_id: str) -> str:
    order_id = order_id.strip().upper()
    order_id = re.sub(r"[^\w-]", "", order_id)
    return order_id


def order_lookup(order_id: str):
    normalized_id = normalize_order_id(order_id)

    orders, snapshot_at = load_orders()

    for order in orders:
        if order["order_id"] == normalized_id:

            result = {
                "order_id": order["order_id"],
                "membership_tier": order["membership_tier"],
                "items": [
                    {
                        "name": item["name"],
                        "quantity": item["quantity"],
                        "final_sale": item["final_sale"]
                    }
                    for item in order["items"]
                ],
                "placed_at": order["placed_at"],
                "status": order["status"],
                "status_updated_at": order["status_updated_at"],
                "shipped_at": order["shipped_at"],
                "delivered_at": order["delivered_at"],
                "carrier": order["carrier"],
                "tracking_number": order["tracking_number"],
                "estimated_delivery": order["estimated_delivery"],
                "customer_safe_message": order["customer_safe_message"]
            }

            return {
                "found": True,
                "snapshot_at": snapshot_at,
                "order": result
            }

    return {
        "found": False,
        "order_id": normalized_id,
        "message": "Order was not found."
    }