from abc import ABC, abstractmethod


class BaseContextModule(ABC):
    @abstractmethod
    def get_context(self, *args, **kwargs) -> str:
        """
        Abstract method to get context.

        Returns
        -------
        str
            The context as a string, to be interpreted by the application's
            language model.
        """
        pass
