import html
import re


class ResponseFormatter:
    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""

        cleaned = html.unescape(str(text))
        cleaned = ResponseFormatter._replace_symbols(cleaned)
        cleaned = ResponseFormatter._strip_markdown(cleaned)
        cleaned = ResponseFormatter._normalize_lines(cleaned)
        return cleaned.strip()

    @staticmethod
    def for_speech(text: str, max_length: int = 500) -> str:
        cleaned = ResponseFormatter.clean(text)
        cleaned = cleaned.replace("%", " percent ")
        cleaned = cleaned.replace("=", " equals ")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned[:max_length]

    @staticmethod
    def _replace_symbols(text: str) -> str:
        replacements = {
            "\u202f": " ",
            "\u00a0": " ",
            "≈": "about",
            "×": "x",
            "–": "-",
            "—": "-",
            "‑": "-",
            "−": "-",
            "’": "'",
            "“": '"',
            "”": '"',
            "•": "-",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    @staticmethod
    def _strip_markdown(text: str) -> str:
        text = re.sub(r"```(?:\w+)?\s*([\s\S]*?)```", r"\1", text)
        text = re.sub(r"`([^`]+)`", r"\1", text)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"\*([^*\n]+)\*", r"\1", text)
        text = re.sub(r"_([^_\n]+)_", r"\1", text)
        text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"</?[^>]+>", "", text)
        return text

    @staticmethod
    def _normalize_lines(text: str) -> str:
        lines = []
        previous_blank = False

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                if not previous_blank and lines:
                    lines.append("")
                previous_blank = True
                continue

            line = re.sub(r"^\s*[-*+]\s+", "- ", line)
            line = re.sub(r"^\s*\d+[.)]\s+", "- ", line)
            line = re.sub(r"\s+", " ", line)
            lines.append(line)
            previous_blank = False

        normalized = "\n".join(lines)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized
