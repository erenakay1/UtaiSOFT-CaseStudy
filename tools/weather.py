"""Weather tool — OpenWeatherMap API."""

from __future__ import annotations

from typing import Optional, Type

import requests
from pydantic import BaseModel, Field

import config
from registry.models import ToolMetadata
from tools.base import DynamicTool


class WeatherInput(BaseModel):
    city: str = Field(..., description="City name, e.g. 'Istanbul'")
    units: str = Field(default="metric", description="Units: metric | imperial | standard")


class WeatherTool(DynamicTool):
    name: str = "weather"
    description: str = "Get current weather information for a city using OpenWeatherMap."
    args_schema: Type[BaseModel] = WeatherInput

    def _run(self, city: str, units: str = "metric") -> str:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": config.OPENWEATHER_API_KEY,
            "units": units,
            "lang": "tr",
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            city_name = data["name"]
            country = data["sys"]["country"]

            unit_symbol = "°C" if units == "metric" else ("°F" if units == "imperial" else "K")
            speed_unit = "m/s" if units != "imperial" else "mph"

            return (
                f"📍 {city_name}, {country}\n"
                f"🌤 Durum: {weather_desc}\n"
                f"🌡 Sıcaklık: {temp}{unit_symbol} (hissedilen: {feels_like}{unit_symbol})\n"
                f"💧 Nem: %{humidity}\n"
                f"💨 Rüzgar: {wind_speed} {speed_unit}"
            )
        except requests.RequestException as e:
            return f"Hava durumu alınamadı: {e}"

