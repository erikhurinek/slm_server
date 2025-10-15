from .name_generator import NameGenerator


class Message:
    """
    A class representing a message in the chat application.

    Attributes
    ----------
    role : str
        The role of the message sender: "system", "user", or "assistant".
    content : str
        The content of the message.
    id : str or int
        The unique identifier for the message.
    user_id : str or int
        The ID of the user who sent the message.
        Set automatically to "system" or "assistant" for those roles.
    user_name : str
        A human-readable name for the user, generated from the user_id.
    hidden : bool
        Whether the message should be hidden from clients.
    """

    def __init__(self, role, content, message_id, user_id, hidden=False):
        """
        Initialize a Message object.

        Parameters
        ----------
        role : str
            The role of the message sender: "system", "user", or "assistant".
        content : str
            The content of the message.
        message_id : str or int
            The unique identifier for the message.
        user_id : str or int
            The ID of the user who sent the message.
            Set automatically to "system" or "assistant" for those roles.
        hidden : bool, optional
            Whether the message should be hidden from clients. Default is
            False.
        """
        self.role = role
        self.content = content
        self.id = message_id
        if role == "system":
            self.user_id = "system"
        elif role == "assistant":
            self.user_id = "assistant"
        else:
            self.user_id = user_id
        self.user_name = NameGenerator.generate_name(self.user_id)
        self.hidden = hidden

    def to_dict(self, include_user_name=False) -> dict:
        """
        Convert the Message object to a dictionary representation, for use in
        transmission to clients.

        Parameter
        ----------
        include_user_name : bool
            Whether to include the user_name in the dictionary representation.
            Default is False.

        Returns
        -------
        dict
            A dictionary representation of the Message object.
        """
        data = {
            "role": self.role,
            "content": self.content,
            "id": self.id,
            "hidden": self.hidden,
            "user_id": self.user_id,
        }
        if include_user_name:
            data["user_name"] = self.user_name
        return data

    def __repr__(self):
        return (
            f"Message(role={self.role}, content={self.content},"
            f"id = {self.id}, hidden = {self.hidden}"
        )
