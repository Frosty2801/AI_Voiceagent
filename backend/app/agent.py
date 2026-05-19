from typing import Tuple, Dict, List

# Minimal Agent stub that keeps in-memory session history (last 7 messages)
class Agent:
    def __init__(self):
        self.sessions: Dict[str, List[str]] = {}

    async def handle_message(self, session_id: str, message: str) -> Tuple[str, bool, str | None]:
        history = self.sessions.get(session_id, [])
        history.append(message)
        # keep only last 7 messages
        history = history[-7:]
        self.sessions[session_id] = history

        # Simple rule: if message contains 'calc:' use calculator tool
        if message.strip().lower().startswith("calc:"):
            expr = message.split("calc:", 1)[1].strip()
            try:
                # very simple and unsafe eval for scaffold only
                result = str(eval(expr, {"__builtins__": {}}))
                reply = f"Calculator result: {result}"
                return reply, True, "calculator"
            except Exception:
                return "Calculator error: invalid expression.", True, "calculator"

        # web search stub trigger
        if message.strip().lower().startswith("search:"):
            q = message.split("search:", 1)[1].strip()
            # stubbed response
            reply = f"Search stub results for '{q}': (stubbed result 1; stubbed result 2)"
            return reply, True, "web_search"

        # default: echo with small transformation
        reply = f"Echo (agent stub): I received your message: '{message}'"
        return reply, False, None
