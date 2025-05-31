import os
import json
from typing import Any

CONFIG_FILE_NAME = "config.json"


class Settings:
    """
    Singleton class to manage application settings.
    """

    _instance = None

    _default = {
        "debug": True,
        "model": "gemma3:1b",
        "port": 8080,
        "force_prompt": "<FORCE_CONTINUE>",
        "system_prompt": (
            "You are a witty AI. Sometimes, you may respond with sarcasm. Be as human as possible. "
            + "Each user prompt starts with their name, followed by a colon and their prompt. Your responses must not start with a name followed by a colon. You are responding to all users. Occasionally, users may respond with "
            + "<FORCE_CONTINUE>"
            + " which is an automatically generated message, indicating that you should continue where you left off. Do not use emojis or narration in your responses."
        ),
        "greeting": "Hello.",
        "hide_system_prompt": True,
        "show_user_name": True,
        "context_pretext": "Let me take a moment to read the context that will be sent. I'll tell you when I'm ready to continue.",
        "context_modules": []
    }
    _config = {}
    _root: str | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._load_config()
        self._sync_config()

    @classmethod
    def get_root(cls) -> str:
        """
        Gets the root application directory.

        Returns
        -------
        str
            The root directory where the config file is saved and loaded from.

        Raises
        ------
        ValueError
            If the root directory is not set. You must set it using `Settings.set_root()`, ideally at the start of the application.
        """
        if cls._root is None:
            raise ValueError("Root directory is not set. Please set it using Settings.set_root()")
        return cls._root

    @classmethod
    def set_root(cls, root: str) -> None:
        """
        Set the root directory for the settings, which is used to determine where the config file is saved and loaded from.

        Parameters
        ----------
        root : str
            The root directory to set.
        """
        cls._root = root

    @classmethod
    def get(cls, key: str) -> Any:
        """
        Get the value of a setting by key.

        Parameters
        ----------
        key : str
            The key of the setting to retrieve. This is case-sensitive and usually lowercase. If the key is not found, it will try to search for a default value, or raise a KeyError if the key is unrecognized.

        Raises
        ------
        KeyError
            If the key is unrecognized and does not exist in the default settings.

        Returns
        -------
        The value of the setting, or the default value if the key does not exist.
        """
        if key in cls()._config:
            return cls()._config[key]
        elif key in cls()._default:
            return cls()._default[key]
        else:
            raise KeyError(f"Setting '{key}' is unrecognized.")

    def _save_config(self):
        """
        Save the current configuration to the config file.
        """
        config_path = os.path.join(self.get_root(), CONFIG_FILE_NAME)
        with open(config_path, "w") as config_file:
            json.dump(self._config, config_file, indent=4)

    def _load_config(self):
        """
        Load the configuration from the config file.
        If the file does not exist, it will create a new one with default settings.
        """
        config_path = os.path.join(self.get_root(), CONFIG_FILE_NAME)
        if not os.path.exists(config_path):
            self._save_config()
            self._sync_config()
            return

        with open(config_path, "r") as config_file:
            self._config = json.load(config_file)

    def _sync_config(self):
        """
        Synchronize the current configuration with the default settings.
        This will add missing keys to the current configuration and save it.
        """
        for key, value in self._default.items():
            if key not in self._config:
                self._config[key] = value
        self._save_config()
