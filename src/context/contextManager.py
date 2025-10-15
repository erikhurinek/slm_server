import os

from .modules.base_context_module import BaseContextModule
from ..settings import Settings


class ContextManager:
    """
    Singleton class to manage and provide context from various context modules.
    """
    _instance = None

    _registered_context_modules: dict[str, BaseContextModule] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContextManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    @staticmethod
    def _snake_to_pascal_case(name: str) -> str:
        """
        Convert a snake_case string to PascalCase.

        Parameters
        ----------
        name : str
            The snake_case string to convert.

        Returns
        -------
        str
            The converted PascalCase string.
        """
        return "".join(word.capitalize() for word in name.split("_"))

    @classmethod
    def register_context_modules(cls, context_modules: list[dict]) -> None:
        """
        Register context modules to the ContextManager.

        Parameters
        ----------
        context_modules : list[dict]
            A list of context module information to register.
            Each module entry should contain a `name` field that matches the
            name of the module file, and any additional arguments.
        """

        module_folder = os.path.join(
            Settings.get_root(), "src", "context", "modules")

        for data in context_modules:
            if "name" not in data:
                raise KeyError(
                    "Context module data must contain a 'name' field.")

            module_name = data["name"]
            module_path = os.path.join(module_folder, f"{module_name}.py")
            if not os.path.exists(module_path):
                raise FileNotFoundError(
                    f"Context module {module_name} not found at {module_path}")

            module = __import__(f"src.context.modules.{
                                module_name}", fromlist=[module_name])
            class_name = cls._snake_to_pascal_case(module_name)
            context_class = getattr(module, class_name, None)
            if context_class is None:
                raise ImportError(
                    f"Class {class_name} not found in module {module_name}")
            if not issubclass(context_class, BaseContextModule):
                raise TypeError(
                    f"Class {class_name} in module {module_name} must inherit"
                    f"from BaseContextModule")

            instance = context_class(**data)
            cls()._registered_context_modules[module_name] = instance

    @classmethod
    def get_context(cls, *args, **kwargs) -> str:
        """
        Get the context from all registered context modules.

        Returns
        -------
        str
            The combined context from all registered modules.
        """
        contexts = []
        for module in cls()._registered_context_modules.values():
            contexts.append(module.get_context(*args, **kwargs))

        if len(contexts) == 0:
            return ("Please repeat and tell the users that there was an issue"
                    "getting the context, and you cannot provide anything"
                    "useful.")
        else:
            return ("Here is some context to be analysed. Please use this in"
                    "your responses. \n" + "\n".join(contexts))
