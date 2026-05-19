from dataclasses import dataclass
from typing import Any


class ToolError(Exception):
    pass


@dataclass(frozen=True)
class ToolResult:
    name: str
    output: str
    meta: dict[str, Any]
