import logging
import sys
from dotenv import load_dotenv

from config import load_config
from wb_api import get_orders_for_date, parse_order
from storage import init_db, save_to_db, save_to_csv, get_top_articles
from telegram_bot import send_top_articles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    load_dotenv()
    cfg = load_config()

    raw_orders, report_date = get_orders_for_date(cfg.wb_api_token)
    logger.info(f"Fetched {len(raw_orders)} orders for {report_date}.")

    orders = []
    for raw in raw_orders:
        try:
            orders.append(parse_order(raw))
        except ValueError as e:
            logger.warning(f"Skipping malformed order: {e}")

    if not orders:
        logger.warning("No valid orders to process. Skipping.")
        return

    init_db(cfg.db_path)
    inserted = save_to_db(orders, cfg.db_path)
    save_to_csv(orders, cfg.csv_path, report_date)
    logger.info(f"Saved {inserted} new orders (skipped {len(orders) - inserted} duplicates). CSV exported.")

    top = get_top_articles(orders)
    send_top_articles(cfg.telegram_bot_token, cfg.telegram_chat_id, top, total_orders=len(orders), report_date=report_date)
    logger.info("Telegram notification sent.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
