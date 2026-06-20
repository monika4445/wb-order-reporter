import time
import logging
import requests
from datetime import datetime, timedelta, date

logger = logging.getLogger(__name__)

WB_ORDERS_URL = "https://statistics-api.wildberries.ru/api/v1/supplier/orders"
TIMEOUT = 30
MAX_RETRIES = 3


def fetch_orders(token: str, date_from: str) -> list[dict]:
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                WB_ORDERS_URL,
                headers={"Authorization": token},
                params={"dateFrom": date_from, "flag": 1},
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise
            wait = 2 ** attempt
            logger.warning(f"WB API request failed (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {wait}s: {e}")
            time.sleep(wait)
    raise RuntimeError("Unreachable")


def get_orders_for_date(token: str, target_date: date | None = None) -> tuple[list[dict], date]:
    if target_date is None:
        target_date = (datetime.now() - timedelta(days=1)).date()
    date_from = f"{target_date}T00:00:00"
    orders = fetch_orders(token, date_from)
    return [o for o in orders if datetime.fromisoformat(o["date"]).date() == target_date], target_date


def parse_order(order: dict) -> dict:
    price = order.get("totalPrice", 0)
    is_cancel = order.get("isCancel", False)
    raw_date = order.get("date")
    if not raw_date:
        raise ValueError(f"Order missing 'date' field: {order.get('srid', 'unknown')}")

    return {
        "srid": order.get("srid", ""),
        "order_date": datetime.fromisoformat(raw_date).strftime("%d-%m-%Y"),
        "article": order.get("supplierArticle", ""),
        "product_name": order.get("subject", ""),
        "status": "Отменён" if is_cancel else "Новый",
        "price": round(float(price or 0), 2),
    }
