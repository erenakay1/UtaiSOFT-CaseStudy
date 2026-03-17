"""End-to-end tests for the full agent pipeline.

NOTE: Requires all API keys and Pinecone index to be set up.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


@pytest.mark.integration
class TestAgentE2E:
    """Full pipeline tests."""

    @pytest.fixture(autouse=True)
    def setup_graph(self):
        from tools.loader import load_all_tools
        from agent.graph import build_graph

        self.registry = load_all_tools()
        self.graph = build_graph(self.registry)

    def _run_query(self, query: str) -> dict:
        return self.graph.invoke({"user_query": query})

    def test_weather_query(self):
        result = self._run_query("İstanbul'da hava nasıl?")
        assert result.get("selected_tool") == "weather"
        assert result.get("final_response") is not None

    def test_currency_query(self):
        result = self._run_query("100 dolar kaç TL?")
        assert result.get("selected_tool") == "currency"
        assert result.get("final_response") is not None

    def test_code_executor_query(self):
        result = self._run_query("Python ile 10'un faktöriyelini hesapla")
        assert result.get("selected_tool") == "code_executor"
        assert result.get("final_response") is not None

    def test_translate_query(self):
        result = self._run_query("Hello'yu Türkçe'ye çevir")
        assert result.get("selected_tool") == "translate"
        assert result.get("final_response") is not None

    def test_irrelevant_query(self):
        result = self._run_query("asdflkjasdf random gibberish 12345")
        # Should either find no tool or have low confidence
        final = result.get("final_response", "")
        assert final is not None  # Should still produce some response
