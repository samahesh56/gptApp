class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def to_json(self):
        return {"role": self.role, "content": self.content}

    # Class method to create a Message instance from JSON
    @classmethod
    def from_json(cls, json_data):
        return cls(json_data["role"], json_data["content"])