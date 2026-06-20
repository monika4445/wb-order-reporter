import logging
import requests
from datetime import date

logger = logging.getLogger(__name__)

TELEGRAM_TIMEOUT = 10


def send_top_articles(bot_token: str, chat_id: str, top_articles: list[tuple[str, int]], total_orders: int, report_date: date):
    formatted_date = report_date.strftime("%d.%m.%Y")

    lines = [
        f"📦 Заказы Wildberries за {formatted_date}",
        f"Всего заказов: {total_orders}\n",
        f"🏆 Топ-{len(top_articles)} артикула по количеству заказов:",
    ]
    for i, (article, count) in enumerate(top_articles, start=1):
        lines.append(f"{i}. {article} — {count} шт.")

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": "\n".join(lines)},
            timeout=TELEGRAM_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to send Telegram message: {e}") from e
