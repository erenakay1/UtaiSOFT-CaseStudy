"""IP Lookup tool — ip-api.com (free, no API key required)."""

from __future__ import annotations

from typing import Type

import requests
from pydantic import BaseModel, Field

from tools.base import DynamicTool


class IPLookupInput(BaseModel):
    ip: str = Field(
        default="",
        description="IP address to look up. Leave empty for your own public IP.",
    )


class IPLookupTool(DynamicTool):
    name: str = "ip_lookup"
    description: str = "Look up geolocation and network information for an IP address."
    args_schema: Type[BaseModel] = IPLookupInput

    def _run(self, ip: str = "") -> str:
        try:
            # If no IP provided, the API returns info for the requester's IP
            url = f"http://ip-api.com/json/{ip}" if ip else "http://ip-api.com/json/"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "success":
                return f"IP sorgusu başarısız: {data.get('message', 'Bilinmeyen hata')}"

            return (
                f"🌐 IP Bilgisi\n"
                f"   IP: {data.get('query', 'N/A')}\n"
                f"   Ülke: {data.get('country', 'N/A')} ({data.get('countryCode', '')})\n"
                f"   Şehir: {data.get('city', 'N/A')}, {data.get('regionName', 'N/A')}\n"
                f"   ISP: {data.get('isp', 'N/A')}\n"
                f"   Organizasyon: {data.get('org', 'N/A')}\n"
                f"   Koordinatlar: {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}\n"
                f"   Timezone: {data.get('timezone', 'N/A')}"
            )
        except requests.RequestException as e:
            return f"IP sorgulama hatası: {e}"