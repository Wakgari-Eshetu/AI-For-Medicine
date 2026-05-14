import json
from src.logger import logger
from src.config import MESSAGES_DIR
 
 
def save_to_data_lake(channel: str, date_str: str, messages: list[dict]):
    """Save messages to data/raw/telegram_messages/YYYY-MM-DD/channel.json"""
 
    partition_dir = MESSAGES_DIR / date_str
    partition_dir.mkdir(parents=True, exist_ok=True)
    out_path = partition_dir / f"{channel}.json"
 
    # Merge with existing data to avoid duplicates
    existing = []
    if out_path.exists():
        with open(out_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        existing_ids = {m["message_id"] for m in existing}
        messages = existing + [m for m in messages if m["message_id"] not in existing_ids]
 
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
 
    logger.info(f"Saved {len(messages)} records → {out_path}")