import os
from dataclasses import dataclass


@dataclass
class Config:
    wb_api_token: str
    telegram_bot_token: str
    telegram_chat_id: str
    db_path: str = "orders.db"
    csv_path: str = "orders.csv"


def load_config() -> Config:
    required = ["WB_API_TOKEN", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise EnvironmentError(f"Missing env vars: {', '.join(missing)}")

    return Config(
        wb_api_token=os.environ["WB_API_TOKEN"],
        telegram_bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
        telegram_chat_id=os.environ["TELEGRAM_CHAT_ID"],
    )
