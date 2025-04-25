import eventlet

eventlet.monkey_patch()

import sys


from src.slm_chat_logger import Logger
from src.application import Application

if __name__ == "__main__":
    Logger.info("Starting SLM Server...")

    try:
        app = Application()
        app.run()
    except Exception as e:
        Logger.exception("Fatal error in main loop")
        sys.exit(1)
