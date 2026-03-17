"""Web search tool — Tavily API."""

from __future__ import annotations

from typing import Type

from pydantic import BaseModel, Field
from tavily import TavilyClient

import config
from registry.models import ToolMetadata
from tools.base import DynamicTool


class WebSearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    max_results: int = Field(default=5, description="Number of results to return (1-10)")


class WebSearchTool(DynamicTool):
    name: str = "web_search"
    description: str = "Search the web for information using Tavily."
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str, max_results: int = 5) -> str:
        try:
            client = TavilyClient(api_key=config.TAVILY_API_KEY)
            response = client.search(query=query, max_results=min(max_results, 10))

            results = []
            for i, result in enumerate(response.get("results", []), 1):
                title = result.get("title", "No title")
                url = result.get("url", "")
                content = result.get("content", "")[:200]
                results.append(f"{i}. **{title}**\n   {url}\n   {content}")

            if not results:
                return f"'{query}' için sonuç bulunamadı."

            return f"🔍 '{query}' için arama sonuçları:\n\n" + "\n\n".join(results)

        except Exception as e:
            return f"Web araması başarısız: {e}"

