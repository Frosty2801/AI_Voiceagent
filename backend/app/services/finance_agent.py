import json
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from app.core.memory import ConversationMemory
from app.core.settings import Settings
from app.tools import CurrencyConverter, SafeCalculator, ToolError, ToolResult


SYSTEM_PROMPT = """
You are Finance VoiceAgent, a practical assistant for personal finance questions.
Instructions:
1. Use a clear, concise, educational tone.
2. Do not provide professional financial, investment, legal, or tax advice.
3. Use safe_calculator whenever the user asks for arithmetic, percentages, savings totals, budgets, or projections.
4. Use currency_converter whenever the user asks to convert money between currencies.
5. Ask one short clarification question when required data is missing.
6. Keep answers grounded in the conversation history from the same session.
7. After using a tool, explain the result in natural language and mention assumptions.
"""

TOOL_DECISION_PROMPT = """
Choose whether the assistant must use a tool before answering.
Return only valid JSON with this shape:
{
  "tool": "currency_converter" | "safe_calculator" | "none",
  "arguments": {
    "amount": number,
    "from_currency": "USD",
    "to_currency": "EUR",
    "expression": "250 * 12"
  },
  "reason": "short reason"
}

Tool descriptions:
- currency_converter: {currency_description}
- safe_calculator: {calculator_description}

Conversation history:
{history}

Current user message:
{message}
"""

ANSWER_PROMPT = """
Write the final assistant response.
Conversation history:
{history}

User message:
{message}

Tool used: {tool_name}
Tool result: {tool_output}

Requirements:
- Answer in English.
- Be concise and useful.
- If a tool was used, include the concrete result.
- Include a short reminder that this is educational, not professional financial advice when relevant.
"""


class FinanceAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.memory = ConversationMemory(max_messages=7)
        self.calculator = SafeCalculator()
        self.currency = CurrencyConverter(settings.currency_api_base_url)
        self.llm = self._build_llm()

    async def handle_message(self, session_id: str, message: str) -> dict[str, Any]:
        history = self.memory.get(session_id)
        formatted_history = self.memory.format_for_prompt(history)
        decision = await self._decide_tool(message, formatted_history)
        tool_result = await self._execute_tool(decision)
        reply = await self._create_reply(message, formatted_history, tool_result)
        self.memory.add_turn(session_id, message, reply)

        return {
            "reply": reply,
            "used_tool": tool_result is not None,
            "tool_name": tool_result.name if tool_result else None,
            "meta": tool_result.meta if tool_result else {},
        }

    def _build_llm(self):
        if not self.settings.nvidia_api_key:
            return None
        return ChatNVIDIA(
            model=self.settings.nvidia_model,
            api_key=self.settings.nvidia_api_key,
            base_url=self.settings.nvidia_base_url,
            temperature=0.2,
        )

    async def _decide_tool(self, message: str, history: str) -> dict[str, Any]:
        if self.llm is None:
            return self._fallback_decision(message, history)

        prompt = TOOL_DECISION_PROMPT.format(
            currency_description=self.currency.description,
            calculator_description=self.calculator.description,
            history=history,
            message=message,
        )
        try:
            response = await self.llm.ainvoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
            return self._parse_decision(str(response.content))
        except Exception:
            return self._fallback_decision(message, history)

    async def _execute_tool(self, decision: dict[str, Any]) -> ToolResult | None:
        tool = decision.get("tool")
        args = decision.get("arguments") or {}

        try:
            if tool == "currency_converter":
                return await self.currency.run(
                    amount=float(args["amount"]),
                    from_currency=str(args["from_currency"]),
                    to_currency=str(args["to_currency"]),
                )
            if tool == "safe_calculator":
                return self.calculator.run(str(args["expression"]))
        except (KeyError, ValueError, ToolError) as exc:
            return ToolResult(
                name=str(tool),
                output=f"The tool could not complete the request: {exc}",
                meta={"error": str(exc)},
            )
        return None

    async def _create_reply(self, message: str, history: str, tool_result: ToolResult | None) -> str:
        if self.llm is None:
            return self._fallback_reply(message, tool_result)

        prompt = ANSWER_PROMPT.format(
            history=history,
            message=message,
            tool_name=tool_result.name if tool_result else "none",
            tool_output=tool_result.output if tool_result else "No tool was used.",
        )
        try:
            response = await self.llm.ainvoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
            return str(response.content).strip()
        except Exception:
            return self._fallback_reply(message, tool_result)

    @staticmethod
    def _parse_decision(content: str) -> dict[str, Any]:
        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if not match:
            return {"tool": "none", "arguments": {}, "reason": "No JSON decision returned."}
        try:
            decision = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"tool": "none", "arguments": {}, "reason": "Invalid JSON decision returned."}

        if decision.get("tool") not in {"currency_converter", "safe_calculator", "none"}:
            decision["tool"] = "none"
        decision.setdefault("arguments", {})
        return decision

    def _fallback_decision(self, message: str, history: str = "") -> dict[str, Any]:
        currency = self._extract_currency_request(message)
        if currency:
            amount, source, target = currency
            return {
                "tool": "currency_converter",
                "arguments": {"amount": amount, "from_currency": source, "to_currency": target},
                "reason": "Detected a currency conversion request.",
            }

        expression = self._extract_math_expression(message, history)
        if expression:
            return {
                "tool": "safe_calculator",
                "arguments": {"expression": expression},
                "reason": "Detected a financial calculation request.",
            }

        return {"tool": "none", "arguments": {}, "reason": "No tool needed."}

    @staticmethod
    def _extract_currency_request(message: str) -> tuple[float, str, str] | None:
        pattern = re.compile(
            r"(?P<amount>\d+(?:\.\d+)?)\s*(?P<from>[A-Za-z]{3})\s+(?:to|in|into)\s+(?P<to>[A-Za-z]{3})",
            flags=re.IGNORECASE,
        )
        match = pattern.search(message)
        if not match:
            return None
        return float(match.group("amount")), match.group("from").upper(), match.group("to").upper()

    @staticmethod
    def _extract_math_expression(message: str, history: str = "") -> str | None:
        lowered = message.lower()
        percent_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s+of\s+(\d+(?:\.\d+)?)", lowered)
        if percent_match:
            return f"{percent_match.group(1)} / 100 * {percent_match.group(2)}"

        contextual_percent = re.search(r"(\d+(?:\.\d+)?)\s*%\s+of\s+(?:that|it)", lowered)
        if contextual_percent:
            user_history = " ".join(
                line.removeprefix("User:").strip()
                for line in history.splitlines()
                if line.startswith("User:")
            )
            numbers = re.findall(r"\d+(?:\.\d+)?", user_history)
            if numbers:
                return f"{contextual_percent.group(1)} / 100 * {numbers[-1]}"

        monthly_match = re.search(
            r"(?:save|saving)\s+(\d+(?:\.\d+)?)\D+(?:for|during)\s+(\d+(?:\.\d+)?)\s+months?",
            lowered,
        )
        if monthly_match:
            return f"{monthly_match.group(1)} * {monthly_match.group(2)}"

        math_chars = re.findall(r"[\d\s+\-*/().%]+", message)
        candidate = max((item.strip() for item in math_chars), key=len, default="")
        if len(candidate) >= 3 and re.search(r"\d", candidate) and re.search(r"[+\-*/%]", candidate):
            return candidate.replace("%", "/100")
        return None

    @staticmethod
    def _fallback_reply(message: str, tool_result: ToolResult | None) -> str:
        if tool_result:
            return (
                f"{tool_result.output} This is an educational estimate, not professional financial advice."
            )
        return (
            "I can help with budgeting, savings calculations, and currency conversions. "
            "Ask me something like 'Convert 100 USD to EUR' or 'If I save 250 every month for 12 months, how much will I save?'"
        )
