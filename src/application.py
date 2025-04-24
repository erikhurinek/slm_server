from . import settings
from .message import Message
from .ai_chat_generator import AiChatGenerator

from flask import Flask, Response, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import eventlet


class Application:
    def __init__(self):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)

        # Create an application context for initialization
        with self.app.app_context():
            self.messages = [Message("system", settings.SYSTEM_PROMPT, 0)]
            self.messageId = 1
            self.clients = {}
            self.ai_chat_generator = AiChatGenerator(self.slm_token_callback, self.slm_finish_callback)
            self.ai_chat_target_index = None
            self.ai_busy = False
            self.user_count = 0

            self.make_routes()

    def slm_token_callback(self, new_tokens, full_response):
        """
        Callback function for receiving tokens from the AI model.
        This function is called each time a new token is generated.
        """
        self.messages[self.ai_chat_target_index].content = full_response
        self.update_clients([self.messages[self.ai_chat_target_index].id])

    def slm_finish_callback(self, full_response):
        """
        Callback function for when the AI model finishes generating a response.
        This function is called when the generation is complete.
        """
        self.messages[self.ai_chat_target_index].content = full_response
        self.update_clients([self.messages[self.ai_chat_target_index].id])
        self.set_ai_busy(False)

    def request_slm_background_response(self):
        """
        Request a background response for the current messages from the AI model.
        """
        if self.ai_chat_generator.request_background_chat(self.messages):
            self.add_message("assistant", "...")
            self.ai_chat_target_index = len(self.messages) - 1
            self.set_ai_busy(True)

    def add_message(self, role, content):
        self.messages.append(Message(role, content, self.messageId))
        self.messageId += 1

    def update_clients(self, messageIds=None, clientIds=None):
        """
        Update clients with new messages.
        ### Parameters:
        - messageIds: List of message IDs to send to the clients. If None, the last message ID is used.
        - clientIds: List of client IDs to send the messages to. If None, all clients are updated.
        """
        clientIds = clientIds or self.clients.keys()
        messageIds = messageIds or [self.messageId - 1]
        for clientId in clientIds:
            if clientId in self.clients:
                new_messages = []
                for message in self.messages:
                    if message.id in messageIds:
                        new_messages.append(message.to_dict())

                self.socketio.emit("new_messages", {"new_messages": new_messages}, room=clientId)

    def broadcast_user_count(self):
        """Broadcast the current user count to all clients"""
        self.socketio.emit("user_count", {"count": self.user_count})

    def set_ai_busy(self, busy):
        """Set AI busy status and broadcast to all clients"""
        self.ai_busy = busy
        self.socketio.emit("ai_status", {"busy": self.ai_busy})

    def reset_clients(self):
        """Reset all clients by sending them the current messages"""
        for clientId in self.clients:
            self.socketio.emit("reset", room=clientId)
    
    def make_routes(self):
        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.socketio.on("connect")
        def handle_connect(auth=None):  # Accept the auth parameter that Flask-SocketIO passes
            print(f"Client connected: {request.sid}")
            self.clients[request.sid] = request.namespace
            self.user_count += 1
            self.broadcast_user_count()
            self.update_clients(range(self.messageId))
            # Send current AI status to the new client
            self.socketio.emit("ai_status", {"busy": self.ai_busy}, room=request.sid)

        @self.socketio.on("disconnect")
        def handle_disconnect():
            print(f"Client disconnected: {request.sid}")
            if request.sid in self.clients:
                del self.clients[request.sid]
                self.user_count -= 1
                self.broadcast_user_count()

        @self.socketio.on("submit_message")
        def handle_message(data):
            """Handles message submission from the client."""
            print(f"Message from {request.sid}: {data}")
            content = data.get("content")
            if not content:
                return
            self.add_message("user", content)
            self.update_clients([self.messageId - 1])
            self.request_slm_background_response()
            print("messages:", self.messages)

        @self.socketio.on("reset")
        def handle_reset():
            """Handles reset chat request from the client."""
            print(f"Reset request from {request.sid}")
            self.messages = []
            self.messageId = 0
            self.add_message("system", settings.SYSTEM_PROMPT)
            self.ai_chat_generator.cancel_generation()
            self.set_ai_busy(False)
            self.reset_clients()
            self.update_clients()

        @self.socketio.on("pull_messages")
        def handle_pull_messages(data={}):
            """Handles message pull request from the client."""
            print(f"Pull messages request from {request.sid}")
            id = data.get("id")
            if not id:
                self.update_clients(clientIds=[request.sid])
            else:
                self.update_clients(messageIds=[id], clientIds=[request.sid])

    def run(self):
        if settings.DEBUG:
            # Use socketio.run with eventlet worker instead of app.run
            self.socketio.run(self.app, host="127.0.0.1", port=settings.PORT, debug=True)
        else:
            # For production, also use socketio.run with eventlet
            self.socketio.run(self.app, host="0.0.0.0", port=settings.PORT, debug=False)
