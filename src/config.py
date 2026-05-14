import os
from pathlib import Path
from dotenv import load_dotenv
 
load_dotenv()
 
# Telegram credentials
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")
 
# Channels to scrape
CHANNELS = [
    "CheMed123",
    "lobelia4cosmetics",
    "tikvahpharma",
    "DawaClinicalPharmacy",
    "EthioMedPharmacy",
]
 
# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"
IMAGES_DIR = DATA_DIR / "images"
MESSAGES_DIR = DATA_DIR / "telegram_messages"
LOGS_DIR = BASE_DIR / "logs"
SESSION_DIR = BASE_DIR / "session"
SESSION_PATH = str(SESSION_DIR / "telegram_session")
 
# Auto-create all directories
for d in [DATA_DIR, IMAGES_DIR, MESSAGES_DIR, LOGS_DIR, SESSION_DIR]:
    d.mkdir(parents=True, exist_ok=True)
 
# Scraper settings
MESSAGE_LIMIT = 500
DELAY_BETWEEN_CHANNELS = 2