import httpx

from .types import ToolError, ToolResult


class CurrencyConverter:
    name = "currency_converter"
    description = (
        "Converts money between currencies using current exchange rates. "
        "Parameters: amount, from_currency, to_currency."
    )

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def run(self, amount: float, from_currency: str, to_currency: str) -> ToolResult:
        source = from_currency.upper().strip()
        target = to_currency.upper().strip()
        if amount <= 0:
            raise ToolError("The amount must be greater than zero.")
        if len(source) != 3 or len(target) != 3:
            raise ToolError("Currencies must use ISO 4217 codes like USD, EUR, or COP.")

        try:
            async with httpx.AsyncClient(timeout=12) as client:
                response = await client.get(f"{self.base_url}/{source}")
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            raise ToolError("The currency service is unavailable right now.") from exc

        try:
            rate = float(data["rates"][target])
        except KeyError as exc:
            raise ToolError(f"The currency service did not return a rate for {target}.") from exc

        converted = amount * rate
        rounded = round(converted, 2)
        return ToolResult(
            name=self.name,
            output=f"{amount} {source} is approximately {rounded} {target}.",
            meta={
                "amount": amount,
                "from_currency": source,
                "to_currency": target,
                "converted_amount": rounded,
                "rate": rate,
                "last_update": data.get("time_last_update_utc"),
            },
        )
