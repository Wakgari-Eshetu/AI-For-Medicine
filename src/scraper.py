import asyncio
from datetime import datetime, timezone
 
from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChannelPrivateError
from telethon.tl.types import MessageMediaPhoto
 
from src.config import (API_ID, API_HASH, PHONE, CHANNELS, IMAGES_DIR,
                        DELAY_BETWEEN_CHANNELS, MESSAGE_LIMIT, SESSION_PATH)
from src.logger import logger
from src.saver import save_to_data_lake
 
 
def message_to_dict(message, channel_name: str) -> dict:
    """Convert a Telethon message to a plain dictionary."""
    return {
        "message_id": message.id,
        "channel_name": channel_name,
        "message_date": message.date.isoformat() if message.date else None,
        "message_text": message.text or "",
        "has_media": message.media is not None,
        "is_photo": isinstance(message.media, MessageMediaPhoto),
        "image_path": None,
        "views": message.views or 0,
        "forwards": message.forwards or 0,
        "reply_count": getattr(message.replies, "replies", 0) if message.replies else 0,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }
 
 
async def scrape_channel(client: TelegramClient, channel: str) -> list[dict]:
    """Scrape messages and download images from a single channel."""
    messages_data = []
    channel_image_dir = IMAGES_DIR / channel
    channel_image_dir.mkdir(parents=True, exist_ok=True)
 
    logger.info(f"Starting scrape: {channel}")
 
    try:
        entity = await client.get_entity(channel)
 
        async for message in client.iter_messages(entity, limit=MESSAGE_LIMIT):
            msg_dict = message_to_dict(message, channel)
 
            # Download image if message has a photo
            if msg_dict["is_photo"]:
                image_path = channel_image_dir / f"{message.id}.jpg"
                try:
                    await client.download_media(message.media, file=str(image_path))
                    msg_dict["image_path"] = str(image_path)
                except Exception as e:
                    logger.warning(f"Could not download image {message.id}: {e}")
 
            messages_data.append(msg_dict)
 
        logger.info(f"Done: {channel} — {len(messages_data)} messages")
 
    except ChannelPrivateError:
        logger.error(f"Channel is private or not found: {channel}")
    except FloodWaitError as e:
        logger.warning(f"Rate limited. Sleeping {e.seconds}s …")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        logger.error(f"Error scraping {channel}: {e}")
 
    return messages_data
 
 
async def run():
    """Main runner — loops through all channels."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    logger.info(f"Scrape started | date: {date_str}")
 
    async with TelegramClient(SESSION_PATH, API_ID, API_HASH) as client:
        await client.start(phone=PHONE)
        logger.info("Telegram client connected")
 
        for channel in CHANNELS:
            messages = await scrape_channel(client, channel)
            if messages:
                save_to_data_lake(channel, date_str, messages)
            await asyncio.sleep(DELAY_BETWEEN_CHANNELS)
 
    logger.info("Scrape finished")
 
 
if __name__ == "__main__":
    asyncio.run(run())