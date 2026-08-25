class ConversationMemory:

    def __init__(self):
        self.messages = []

    def add_user_message(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })

    def add_assistant_message(self, message):
        self.messages.append({
            "role": "assistant",
            "content": message
        })

    def get_messages(self):
        return self.messages

    def get_recent_messages(self, limit=6):
        return self.messages[-limit:]

    def get_recent_text(self, limit=6):
        recent = self.get_recent_messages(limit)

        if not recent:
            return ""

        lines = []

        for message in recent:
            role = message["role"].upper()
            content = message["content"]

            lines.append(f"{role}: {content}")

        return "\n".join(lines)

    def clear(self):
        self.messages = []