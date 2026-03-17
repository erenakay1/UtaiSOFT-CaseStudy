"""Tests for individual tools."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from tools.loader import load_all_tools


class TestToolLoader:
    """Tests for tool loading and registration."""

    def test_all_10_tools_loaded(self):
        registry = load_all_tools()
        assert registry.size == 10

    def test_all_tools_have_metadata(self):
        registry = load_all_tools()
        for name in registry.all_names():
            meta = registry.get_metadata(name)
            assert meta is not None
            assert meta.name == name
            assert len(meta.description) > 0
            assert len(meta.display_name) > 0

    def test_all_tools_have_examples(self):
        registry = load_all_tools()
        for name in registry.all_names():
            meta = registry.get_metadata(name)
            assert len(meta.examples) >= 1, f"{name} has no examples"

    def test_embedding_text_non_empty(self):
        registry = load_all_tools()
        for meta in registry.all_metadata():
            assert len(meta.embedding_text) > 0

    def test_tool_names_unique(self):
        registry = load_all_tools()
        names = registry.all_names()
        assert len(names) == len(set(names)), "Duplicate tool names found"


class TestToolMetadataContent:
    """Test specific tool metadata for correctness."""

    def setup_method(self):
        self.registry = load_all_tools()

    def test_weather_tool_metadata(self):
        meta = self.registry.get_metadata("weather")
        assert meta is not None
        assert "weather" in meta.description.lower() or "hava" in meta.description.lower()
        assert meta.category == "information"

    def test_currency_tool_metadata(self):
        meta = self.registry.get_metadata("currency")
        assert meta is not None
        assert meta.category == "utility"

    def test_code_executor_metadata(self):
        meta = self.registry.get_metadata("code_executor")
        assert meta is not None
        assert meta.category == "computation"

    def test_email_tool_metadata(self):
        meta = self.registry.get_metadata("email")
        assert meta is not None
        assert meta.category == "communication"
