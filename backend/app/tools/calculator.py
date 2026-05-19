import ast
import operator

from .types import ToolError, ToolResult


class SafeCalculator:
    name = "safe_calculator"
    description = (
        "Evaluates arithmetic expressions for financial calculations. "
        "Parameters: expression, a math expression using numbers and +, -, *, /, %, **, parentheses."
    )

    _operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def run(self, expression: str) -> ToolResult:
        if not expression or len(expression) > 160:
            raise ToolError("The expression is empty or too long.")

        try:
            tree = ast.parse(expression, mode="eval")
            value = self._eval(tree.body)
        except Exception as exc:
            raise ToolError("The calculator could not evaluate that expression safely.") from exc

        result = round(value, 4) if isinstance(value, float) else value
        return ToolResult(
            name=self.name,
            output=f"{expression} = {result}",
            meta={"expression": expression, "result": result},
        )

    def _eval(self, node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in self._operators:
            left = self._eval(node.left)
            right = self._eval(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 8:
                raise ToolError("Exponent is too large.")
            return self._operators[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in self._operators:
            return self._operators[type(node.op)](self._eval(node.operand))
        raise ToolError("Only numeric arithmetic expressions are allowed.")
