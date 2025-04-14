class Message:
    """
    A class representing a message in the chat application.
    ### Members:
    role: The role of the message sender: "system", "user", or "assistant".  
    content: The content of the message.  
    message_id: The unique identifier for the message.  
    """
    def __init__(self, role, content, message_id):
        self.role = role
        self.content = content
        self.id = message_id

    def to_dict(self):
        """
        Convert the Message object to a dictionary representation.
        ### Returns:
        A dictionary representation of the Message object.
        """
        return {
            "role": self.role,
            "content": self.content,
            "id": self.id
        }
    
    def __repr__(self):
        return f"Message(role={self.role}, content={self.content}, id={self.id})"