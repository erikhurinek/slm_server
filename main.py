import eventlet

eventlet.monkey_patch()

import sys


from src.logging_utils import create_logger
from src.application import Application

if __name__ == "__main__":
    logger = create_logger()
    logger.info("Starting SLM Server...")

    try:
        app = Application(logger)
        app.run()
    except Exception as e:
        logger.exception("Fatal error in main loop")
        sys.exit(1)
