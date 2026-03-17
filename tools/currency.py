"""Currency converter tool — ExchangeRate-API."""

from __future__ import annotations

from typing import Type

import requests
from pydantic import BaseModel, Field

import config
from registry.models import ToolMetadata
from tools.base import DynamicTool


class CurrencyInput(BaseModel):
    amount: float = Field(..., description="Amount to convert")
    from_currency: str = Field(..., description="Source currency code, e.g. 'USD'")
    to_currency: str = Field(..., description="Target currency code, e.g. 'TRY'")


class CurrencyTool(DynamicTool):
    name: str = "currency"
    description: str = "Convert between currencies using real-time exchange rates."
    args_schema: Type[BaseModel] = CurrencyInput

    def _run(self, amount: float, from_currency: str, to_currency: str) -> str:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        url = f"https://v6.exchangerate-api.com/v6/{config.EXCHANGE_RATE_API_KEY}/pair/{from_currency}/{to_currency}/{amount}"

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get("result") != "success":
                return f"Döviz çevirme hatası: {data.get('error-type', 'unknown')}"

            rate = data["conversion_rate"]
            converted = data["conversion_result"]

            return (
                f"💱 Döviz Çevirme\n"
                f"   {amount:,.2f} {from_currency} = {converted:,.2f} {to_currency}\n"
                f"   Kur: 1 {from_currency} = {rate:,.4f} {to_currency}"
            )
        except requests.RequestException as e:
            return f"Döviz kuru alınamadı: {e}"

