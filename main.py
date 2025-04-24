# Apply eventlet monkey patching before any other imports
import eventlet
eventlet.monkey_patch()

import logging
import os
import sys
from datetime import datetime

# Configure logging
def setup_logging():
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a timestamp for the log filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'slm_server_{timestamp}.log')
    
    # Configure the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler for all logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # Console handler for INFO+ logs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Now import and run the application
from src.application import Application

if __name__ == "__main__":
    # Setup logging
    logger = setup_logging()
    logger.info("Starting SLM Server...")
    
    try:
        app = Application(logger)
        app.run()
    except Exception as e:
        logger.exception("Fatal error in main loop")
        sys.exit(1)
