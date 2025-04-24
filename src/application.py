from . import settings
from .message import Message
from .ai_chat_generator import AiChatGenerator

from flask import Flask, request, render_template
from flask_socketio import SocketIO
import logging


class Application:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)
        self.logger.info("Initializing application")

        with self.app.app_context():
            self.reset_messages()
            self.clients = {}
            self.ai_chat_generator = AiChatGenerator(self.slm_token_callback, self.slm_finish_callback)
            self.ai_chat_target_index = None
            self.ai_busy = False
            self.user_count = 0
            self.ai_enabled = True

            self.make_routes()
            self.logger.info(f"Application initialized with model: {settings.MODEL}")

    def reset_messages(self):
        self.messages = [Message("system", settings.SYSTEM_PROMPT, 0, None, settings.HIDE_SYSTEM_PROMPT)]
        self.messageId = 1
        if (settings.GREETING and settings.GREETING != ""):
            self.add_message("assistant", settings.GREETING)
    
    def slm_token_callback(self, new_tokens, full_response):
        """
        Callback function for receiving tokens from the AI model.
        This function is called each time a new token is generated.
        """
        self.messages[self.ai_chat_target_index].content = full_response
        self.update_clients_append(self.messages[self.ai_chat_target_index].id, new_tokens)

    def slm_finish_callback(self, full_response):
        """
        Callback function for when the AI model finishes generating a response.
        This function is called when the generation is complete.
        """
        # Update message only if an index exists. The referenced message may have been deleted.
        if self.ai_chat_target_index is not None:
            self.messages[self.ai_chat_target_index].content = full_response
            self.update_clients([self.messages[self.ai_chat_target_index].id])
        self.set_ai_busy(False)
        self.logger.info(f"AI response completed: {full_response}")

    def request_slm_background_response(self):
        """
        Request a background response for the current messages from the AI model.
        """
        self.logger.info("Requesting AI response")
        if self.ai_chat_generator.request_background_chat(self.messages):
            self.add_message("assistant", "...")
            self.ai_chat_target_index = len(self.messages) - 1
            self.set_ai_busy(True)
        else:
            self.logger.warning("Failed to request AI response - model may be busy")

    def add_message(self, role, content, user_id=None, hidden=False):
        self.messages.append(Message(role, content, self.messageId, user_id, hidden=False))
        self.messageId += 1
        self.logger.debug(f"Added {role} message: {content[:50]}...")

    def update_clients_append(self, messageId, content_to_append, clientIds=None):
        """
        Append data to the clients.
        ### Parameters:
        - data_to_append: Data to append to the clients.
        - clientIds: List of client IDs to send the messages to. If None, all clients are updated.
        """
        data = [{
            "id": messageId,
            "content": content_to_append,
            "role": self.messages[messageId].role,
            "append": True
        }]
        clientIds = clientIds or self.clients.keys()

        if messageId >= len(self.messages) or not self.messages[messageId]:
            self.logger.warning(f"Message ID {messageId} not found, not appending")
            return
        elif self.messages[messageId].hidden:
            self.logger.warning(f"Message ID {messageId} is hidden, not appending")
            return
        
        for clientId in clientIds:
            if clientId in self.clients:
                self.socketio.emit("update_messages", {"messages": data}, room=clientId)
            else:
                self.logger.warning(f"Client ID {clientId} not found in clients list")
        
        self.logger.debug(f"Appended data \"{content_to_append}\" to clients {clientIds}")

    def update_clients(self, messageIds=None, clientIds=None):
        """
        Update clients with new messages.
        ### Parameters:
        - messageIds: List of message IDs to send to the clients. If None, the last message ID is used.
        - clientIds: List of client IDs to send the messages to. If None, all clients are updated.
        - append: If True, indicates that the message content should be appended to the existing messages.
        """
        clientIds = clientIds or self.clients.keys()
        messageIds = messageIds or [self.messageId - 1]
        for clientId in clientIds:
            if clientId in self.clients:
                updated_messages = []
                for message in self.messages:
                    if message.id in messageIds and not message.hidden:
                        updated_messages.append(message.to_dict())

                self.socketio.emit("update_messages", {"messages": updated_messages}, room=clientId)
        
        if messageIds:
            self.logger.debug(f"Updated clients with message IDs: {messageIds}")

    def broadcast_user_count(self):
        """Broadcast the current user count to all clients"""
        self.socketio.emit("user_count", {"count": self.user_count})
        self.logger.debug(f"User count updated: {self.user_count}")

    def set_ai_busy(self, busy):
        """Set AI busy status and broadcast to all clients"""
        self.ai_busy = busy
        self.socketio.emit("ai_status", {"busy": self.ai_busy})
        if busy:
            self.logger.debug("AI status set to busy")
        else:
            self.logger.debug("AI status set to idle")

    def toggle_ai(self, enabled):
        """Toggle AI responses and broadcast to all clients"""
        self.ai_enabled = enabled
        self.socketio.emit("ai_toggle_status", {"enabled": self.ai_enabled})
        self.logger.info(f"AI responses {'enabled' if enabled else 'disabled'}")

    def reset_clients(self):
        """Reset all clients by sending them the current messages"""
        for clientId in self.clients:
            self.socketio.emit("reset", room=clientId)
        self.logger.info("Chat reset for all clients")
    
    def make_routes(self):
        @self.app.route("/slm-chat/")
        def index():
            return render_template("index.html")

        @self.socketio.on("connect")
        def handle_connect(auth=None):
            self.logger.info(f"Client connected: {request.sid} {request.remote_addr}")
            self.clients[request.sid] = request.namespace
            self.user_count += 1
            self.broadcast_user_count()
            self.update_clients(range(self.messageId))
            self.socketio.emit("ai_status", {"busy": self.ai_busy}, room=request.sid)
            self.socketio.emit("ai_toggle_status", {"enabled": self.ai_enabled}, room=request.sid)

        @self.socketio.on("disconnect")
        def handle_disconnect():
            self.logger.info(f"Client disconnected: {request.sid}")
            if request.sid in self.clients:
                del self.clients[request.sid]
                self.user_count -= 1
                self.broadcast_user_count()

        @self.socketio.on("submit_message")
        def handle_message(data):
            """Handles message submission from the client."""
            self.logger.info(f"Message from {request.sid}: {data}")
            content = data.get("content")
            if not content:
                self.logger.warning(f"Received empty message from {request.sid}")
                return
            self.add_message("user", content, request.sid)
            self.update_clients([self.messageId - 1])
            if self.ai_enabled:
                self.request_slm_background_response()
            else:
                self.logger.debug("AI response not requested (AI disabled)")
            
        @self.socketio.on("toggle_ai")
        def handle_toggle_ai(data):
            """Handles toggling AI on/off."""
            self.logger.info(f"Toggle AI request from {request.sid}: {data}")
            enabled = data.get("enabled", True)
            self.toggle_ai(enabled)

        @self.socketio.on("reset")
        def handle_reset():
            """Handles reset chat request from the client."""
            self.logger.info(f"Reset request from {request.sid}")
            self.reset_messages()
            self.ai_chat_target_index = None
            self.ai_chat_generator.cancel_generation()
            self.set_ai_busy(False)
            self.reset_clients()
            self.update_clients()

        @self.socketio.on("force_response")
        def handle_force_response():
            """Handles force response request from the client."""
            self.logger.info(f"Force response request from {request.sid}")
            self.request_slm_background_response()
            
        @self.socketio.on("pull_messages")
        def handle_pull_messages(data={}):
            """Handles message pull request from the client."""
            self.logger.debug(f"Pull messages request from {request.sid}")
            id = data.get("id")
            if not id:
                self.update_clients(clientIds=[request.sid])
            else:
                self.update_clients(messageIds=[id], clientIds=[request.sid])

    def run(self):
        if settings.DEBUG:
            self.logger.info(f"Starting server in DEBUG mode on port {settings.PORT}")
            self.socketio.run(self.app, host="127.0.0.1", port=settings.PORT, debug=True)
        else:
            self.logger.info(f"Starting server in PRODUCTION mode on port {settings.PORT}")
            self.socketio.run(self.app, host="0.0.0.0", port=settings.PORT, debug=False)
