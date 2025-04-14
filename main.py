# Apply eventlet monkey patching before any other imports
import eventlet
eventlet.monkey_patch()

# Now import and run the application
from src.application import Application

if __name__ == "__main__":
    app = Application()
    app.run()
