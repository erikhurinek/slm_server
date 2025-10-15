import eventlet

eventlet.monkey_patch()

import os  # noqa: E402
import sys  # noqa: E402

from src.application import Application  # noqa: E402
from src.slm_chat_logger import Logger   # noqa: E402
from src.settings import Settings        # noqa: E402


Settings.set_root(os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    Logger.info("Starting SLM Server...")

    try:
        app = Application()
        app.run()
    except Exception:
        Logger.exception("Fatal error in main loop")
        sys.exit(1)
