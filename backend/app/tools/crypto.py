from datetime import datetime, timezone

import httpx

from .types import ToolError, ToolResult


class CryptoPriceLookup:
    name = "crypto_price_lookup"
    description = (
        "Gets the current cryptocurrency price and 24 hour change. "
        "Parameters: crypto_id, a CoinGecko coin id like bitcoin or ethereum; "
        "vs_currency, a target currency like usd, eur, or cop."
    )

    aliases = {
        "btc": "bitcoin",
        "bitcoin": "bitcoin",
        "eth": "ethereum",
        "ethereum": "ethereum",
        "sol": "solana",
        "solana": "solana",
        "bnb": "binancecoin",
        "binance": "binancecoin",
        "ada": "cardano",
        "cardano": "cardano",
        "xrp": "ripple",
        "ripple": "ripple",
        "doge": "dogecoin",
        "dogecoin": "dogecoin",
    }

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def run(self, crypto_id: str, vs_currency: str = "usd") -> ToolResult:
        coin = self._normalize_crypto(crypto_id)
        currency = vs_currency.lower().strip()
        if not coin:
            raise ToolError("The cryptocurrency is required.")
        if not currency or len(currency) < 3:
            raise ToolError("The target currency must be a code like usd, eur, or cop.")

        try:
            async with httpx.AsyncClient(timeout=12) as client:
                response = await client.get(
                    f"{self.base_url}/simple/price",
                    params={
                        "ids": coin,
                        "vs_currencies": currency,
                        "include_24hr_change": "true",
                        "include_last_updated_at": "true",
                    },
                )
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            raise ToolError("The crypto price service is unavailable right now.") from exc

        if coin not in data or currency not in data[coin]:
            raise ToolError(f"No crypto price was found for {coin} in {currency.upper()}.")

        price = float(data[coin][currency])
        change_key = f"{currency}_24h_change"
        change_24h = data[coin].get(change_key)
        last_updated_at = data[coin].get("last_updated_at")
        readable_time = self._format_timestamp(last_updated_at)

        change_text = ""
        if isinstance(change_24h, (int, float)):
            change_text = f" The 24 hour change is {round(change_24h, 2)} percent."

        return ToolResult(
            name=self.name,
            output=(
                f"{coin.title()} is approximately {round(price, 4)} {currency.upper()}."
                f"{change_text}"
            ),
            meta={
                "crypto_id": coin,
                "vs_currency": currency,
                "price": price,
                "change_24h": round(change_24h, 4) if isinstance(change_24h, (int, float)) else None,
                "last_updated_at": readable_time,
            },
        )

    @classmethod
    def _normalize_crypto(cls, value: str) -> str:
        cleaned = value.lower().strip()
        return cls.aliases.get(cleaned, cleaned.replace(" ", "-"))

    @staticmethod
    def _format_timestamp(value: int | None) -> str | None:
        if not value:
            return None
        return datetime.fromtimestamp(value, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
