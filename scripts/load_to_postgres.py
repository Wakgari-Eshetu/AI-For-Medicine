import os
import json
import logging
from pathlib import Path
from datetime import datetime
 
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
 
load_dotenv()
 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent
MESSAGES_DIR = BASE_DIR / "data" / "raw" / "telegram_messages"
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "dbname": os.getenv("POSTGRES_DB", "medical_warehouse"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
}
 
CREATE_SCHEMA_SQL = "CREATE SCHEMA IF NOT EXISTS raw;"
 
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw.telegram_messages (
    message_id      BIGINT,
    channel_name    TEXT,
    message_date    TIMESTAMPTZ,
    message_text    TEXT,
    has_media       BOOLEAN,
    is_photo        BOOLEAN,
    image_path      TEXT,
    views           INTEGER DEFAULT 0,
    forwards        INTEGER DEFAULT 0,
    reply_count     INTEGER DEFAULT 0,
    scraped_at      TIMESTAMPTZ,
    PRIMARY KEY (message_id, channel_name)
);
"""
 
INSERT_SQL = """
INSERT INTO raw.telegram_messages (
    message_id, channel_name, message_date, message_text,
    has_media, is_photo, image_path,
    views, forwards, reply_count, scraped_at
)
VALUES %s
ON CONFLICT (message_id, channel_name) DO UPDATE SET
    views       = EXCLUDED.views,
    forwards    = EXCLUDED.forwards,
    reply_count = EXCLUDED.reply_count,
    scraped_at  = EXCLUDED.scraped_at;
"""
 
 
def collect_all_records() -> list[tuple]:
    """Walk the data lake and collect all message records."""
    records = []
    for json_file in sorted(MESSAGES_DIR.rglob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            messages = json.load(f)
        for m in messages:
            records.append((
                m.get("message_id"),
                m.get("channel_name"),
                m.get("message_date"),
                m.get("message_text", ""),
                m.get("has_media", False),
                m.get("is_photo", False),
                m.get("image_path"),
                m.get("views", 0),
                m.get("forwards", 0),
                m.get("reply_count", 0),
                m.get("scraped_at"),
            ))
    logger.info(f"Collected {len(records)} total records from data lake")
    return records
 
 
def load_to_postgres(records: list[tuple]) -> None:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(CREATE_SCHEMA_SQL)
                cur.execute(CREATE_TABLE_SQL)
                if records:
                    execute_values(cur, INSERT_SQL, records, page_size=500)
                    logger.info(f"✔ Upserted {len(records)} rows into raw.telegram_messages")
                else:
                    logger.warning("No records to insert.")
    finally:
        conn.close()
 
 
if __name__ == "__main__":
    logger.info("═══ Loading raw data to PostgreSQL ═══")
    records = collect_all_records()
    load_to_postgres(records)
    logger.info("═══ Done ═══")