from dataclasses import dataclass, field


@dataclass
class ConversationMemory:
    max_messages: int = 7
    sessions: dict[str, list[dict[str, str]]] = field(default_factory=dict)

    def get(self, session_id: str) -> list[dict[str, str]]:
        return self.sessions.get(session_id, []).copy()

    def add_turn(self, session_id: str, user_message: str, assistant_message: str) -> None:
        history = self.sessions.get(session_id, [])
        history.extend(
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message},
            ]
        )
        self.sessions[session_id] = history[-self.max_messages :]

    @staticmethod
    def format_for_prompt(history: list[dict[str, str]]) -> str:
        if not history:
            return "No previous messages in this session."

        lines = []
        for item in history:
            role = "User" if item["role"] == "user" else "Assistant"
            lines.append(f"{role}: {item['content']}")
        return "\n".join(lines)
