import csv
import sqlite3
from collections import Counter
from datetime import datetime, date
from pathlib import Path

FIELDNAMES = ["order_date", "article", "product_name", "status", "price"]


def init_db(db_path: str):
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                srid TEXT UNIQUE,
                order_date TEXT,
                article TEXT,
                product_name TEXT,
                status TEXT,
                price REAL,
                inserted_at TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_order_date ON orders(order_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_article ON orders(article)")


def save_to_db(orders: list[dict], db_path: str) -> int:
    now = datetime.now().isoformat()
    with sqlite3.connect(db_path) as conn:
        before = conn.total_changes
        conn.executemany(
            """INSERT OR IGNORE INTO orders
               (srid, order_date, article, product_name, status, price, inserted_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [(o["srid"], o["order_date"], o["article"], o["product_name"], o["status"], o["price"], now) for o in orders],
        )
        return conn.total_changes - before


def save_to_csv(orders: list[dict], csv_path: str, report_date: date):
    p = Path(csv_path)
    path = p.with_stem(f"{p.stem}_{report_date}")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for o in orders:
            writer.writerow({**o, "price": f"{o['price']:.2f}".replace(".", ",")})


def get_top_articles(orders: list[dict], n: int = 3) -> list[tuple[str, int]]:
    return Counter(o["article"] for o in orders).most_common(n)
