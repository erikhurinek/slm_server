from .name_generator import NameGenerator

class Message:
    """
    A class representing a message in the chat application.
    ### Members:
    role: The role of the message sender: "system", "user", or "assistant".  
    content: The content of the message.  
    message_id: The unique identifier for the message.  
    user_id: The ID of the user who sent the message. If role is "system", this will be ignored and set to "system". Similarly, if role is "assistant", this will be ignored and set to "assistant".  
    user_name: A human-readable name for the user, generated from the user_id.  
    hidden: Whether the message should be hidden from clients.  
    """

    def __init__(self, role, content, message_id, user_id, hidden=False):
        self.role = role
        self.content = content
        self.id = message_id
        if role == "system":
            self.user_id = "system"
        elif role == "assistant":
            self.user_id = "assistant"
        else:
            self.user_id = user_id
        self.user_name = NameGenerator.get_instance().get_name(self.user_id)
        self.hidden = hidden

    def to_dict(self, show_user_name=False):
        """
        Convert the Message object to a dictionary representation.
        ### Returns:
        A dictionary representation of the Message object.
        """
        data = {
            "role": self.role,
            "content": self.content,
            "id": self.id,
            "hidden": self.hidden,
            "user_id": self.user_id
        }
        if show_user_name:
            data["user_name"] = self.user_name
        return data

    def __repr__(self):
        return f"Message(role={self.role}, content={self.content}, id={self.id}, hidden={self.hidden}"
