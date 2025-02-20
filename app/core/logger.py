import logging
from logging.handlers import RotatingFileHandler
from .config import settings
import sys
import os

def setup_logger():
    # Create logs directory if it doesn't exist
    if not settings.LOG_FILE:
        settings.LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs", "app.log")
    
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        # Ensure directory has write permissions
        os.chmod(log_dir, 0o755)
    
    logger = logging.getLogger('infrastructure_chatbot')
    logger.setLevel(logging.INFO)  # Set a default log level (INFO)
    
    # File Handler
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10485760,  # 10MB
        backupCount=5,
        mode='a+'  # Append mode with create if not exists
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
