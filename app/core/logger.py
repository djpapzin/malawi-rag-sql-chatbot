import logging
from logging.handlers import RotatingFileHandler
from .config import settings
import sys
import os

def setup_logger():
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    
    logger = logging.getLogger('infrastructure_chatbot')
    logger.setLevel(logging.INFO)  # Set a default log level (INFO)
    
    # File Handler
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s: %(message)s')
    )
    
    logger.handlers = []  # Clear any existing handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()
