# log_handler.py
import logging
from logging.handlers import RotatingFileHandler
import os

LOG_FILENAME = os.getenv("AWS_CREATION_LOG", "aws_creation_log.txt")

logger = logging.getLogger("cloud_capstone")
logger.setLevel(logging.INFO)

# Rotating handler to avoid unlimited file growth (keeps 5 files of 2MB each)
handler = RotatingFileHandler(LOG_FILENAME, maxBytes=2 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Avoid duplicate handlers when reloading modules
if not logger.handlers:
    logger.addHandler(handler)

def log_info(message: str):
    logger.info(message)
    print(message)

def log_error(message: str):
    logger.error(message)
    print("ERROR:", message)
