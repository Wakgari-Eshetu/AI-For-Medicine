import logging
from datetime import datetime
from src.config import LOGS_DIR
 
LOGS_DIR.mkdir(parents=True, exist_ok=True)
 
log_file = LOGS_DIR / f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(),
    ],
)
 
logger = logging.getLogger(__name__)