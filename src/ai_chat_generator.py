from . import settings
from .message import Message
from .name_generator import NameGenerator

import threading
import ollama


class AiChatGenerator:
    def __init__(self, token_callback: callable = None, finish_callback: callable = None):
        """
        Initialize the AiChatGenerator with a token callback function.
        ### Parameters:
        - token_callback: A function that will be called each time a new token is generated. (new_tokens, full_generation) => None
        - finish_callback: A function that will be called when the generation is finished. (full_generation) => None
        """
        self.SYSTEM_PROMPT = settings.SYSTEM_PROMPT
        self.MODEL = settings.MODEL
        self.is_generating = False
        self.token_callback = token_callback
        self.finish_callback = finish_callback
        self.lock = threading.Lock()
        self.generation_thread = None
        self.nameGenerator = NameGenerator()

    def _convert_message_to_ollama(self, message: Message):
        """
        Convert a Message object to the format expected by the Ollama API.
        ### Parameters:
        - message: The Message object to convert.
        ### Returns:
        A dictionary representation of the message in the format expected by the Ollama API.
        """

        new_message = ""
        if message.user_id == "system":
            new_message = "System: " + message.content
        elif message.user_id == "assistant":
            new_message = message.content
        else:
            new_message = f"{self.nameGenerator.get_name(message.user_id)}: {message.content}"

        return {"role": message.role, "content": new_message}

    def _generate_response(self):
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
                self.token_callback(f"Error generating response: {str(e)}", f"Error generating response: {str(e)}")
                print(f"Error generating response: {str(e)}")
                if settings.DEBUG:
                    raise e
        finally:
            with self.lock:
                self.is_generating = False
                self.generation_thread = None
                if self.finish_callback:
                    self.finish_callback(full_response)

    def request_background_chat(self, messages):
        """
        Request a chat background response from the model.
        ### Parameters:
        - messages: A list of messages to send to the model.
        """
        with self.lock:
            if self.is_generating:
                return False

            self.messages = [self._convert_message_to_ollama(msg) for msg in messages]
            self.generation_thread = threading.Thread(target=self._generate_response)
            self.generation_thread.daemon = True
            self.generation_thread.start()
            return True

    def cancel_generation(self):
        """
        Attempts to cancel the current generation if possible.
        Returns True if generation was in progress and will be stopped, False otherwise.
        """
        with self.lock:
            was_generating = self.is_generating
            self.is_generating = False
            return was_generating
