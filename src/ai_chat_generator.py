import threading
import ollama

from . import settings
from .message import Message
from .slm_chat_logger import Logger


class AiChatGenerator:
    def __init__(self, token_callback: callable = None, finish_callback: callable = None):
        """
        Initialize the AiChatGenerator with a token callback function.

        Parameters
        ----------
        token_callback : callable, optional
            A function that will be called each time a new token is generated.
            Function signature: (new_tokens, full_generation) -> None
        finish_callback : callable, optional
            A function that will be called when the generation is finished.
            Function signature: (full_generation) -> None
        """
        self.finish_callback = finish_callback
        self.generation_thread = None
        self.is_generating = False
        self.lock = threading.Lock()
        self.MODEL = settings.MODEL
        self.SYSTEM_PROMPT = settings.SYSTEM_PROMPT
        self.token_callback = token_callback

    def _convert_message_to_ollama(self, message: Message) -> None:
        new_message = ""
        if message.user_id == "system":
            new_message = "System: " + message.content
        elif message.user_id == "assistant":
            new_message = message.content
        else:
            new_message = f"{message.user_name}: {message.content}"

        return {"role": message.role, "content": new_message}

    def _generate_response(self) -> None:
        with self.lock:
            if self.is_generating:
                return
            self.is_generating = True

        full_response = ""
        try:
            for chunk in ollama.chat(self.MODEL, messages=self.messages, stream=True):
                if chunk and "message" in chunk and "content" in chunk["message"]:
                    content = chunk["message"]["content"]
                    full_response += content
                    if self.token_callback:
                        self.token_callback(content, full_response)
        except Exception as e:
            if self.token_callback:
                self.token_callback(f" Error generating response.")
                Logger.error(f"Error generating response: {str(e)}")
                if settings.DEBUG:
                    raise e
        finally:
            with self.lock:
                self.is_generating = False
                self.generation_thread = None
                if self.finish_callback:
                    self.finish_callback(full_response)

    def request_background_chat(self, messages: list[Message]) -> bool:
        """
        Request a chat background response from the model.

        Parameters
        ----------
        messages : list[Message]
            A list of messages to send to the model.
        """
        with self.lock:
            if self.is_generating:
                return False

            self.messages = [self._convert_message_to_ollama(msg) for msg in messages]
            self.generation_thread = threading.Thread(target=self._generate_response)
            self.generation_thread.daemon = True
            self.generation_thread.start()
            return True

    def cancel_generation(self) -> bool:
        """
        Attempts to cancel the current generation if possible.

        Returns
        -------
        bool
            True if the generation was successfully canceled, False otherwise.
        """
        with self.lock:
            was_generating = self.is_generating
            self.is_generating = False
            return was_generating
