"""Tests for the Tool Registry."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from registry.models import ToolMetadata
from registry.registry import ToolRegistry
from tools.base import DynamicTool


class DummyTool(DynamicTool):
    name: str = "dummy"
    description: str = "A dummy tool for testing."

    def _run(self, **kwargs) -> str:
        return "dummy result"

DUMMY_META = ToolMetadata(
    name="dummy",
    display_name="Dummy Tool",
    description="A dummy tool used for testing purposes.",
    parameters={"input": {"type": "string"}},
    category="test",
    examples=["test query"],
)

class TestToolMetadata:
    """Tests for ToolMetadata model."""

    def test_embedding_text_with_examples(self):
        meta = ToolMetadata(
            name="test",
            display_name="Test",
            description="A test tool.",
            examples=["example 1", "example 2"],
        )
        text = meta.embedding_text
        assert "A test tool." in text
        assert "example 1" in text
        assert "example 2" in text

    def test_embedding_text_without_examples(self):
        meta = ToolMetadata(
            name="test",
            display_name="Test",
            description="A test tool.",
        )
        assert meta.embedding_text == "A test tool."


class TestToolRegistry:
    """Tests for ToolRegistry."""

    def test_register_and_lookup(self):
        registry = ToolRegistry()
        tool = DummyTool()
        meta = DUMMY_META

        registry.register(meta, tool)

        assert registry.size == 1
        assert registry.get_metadata("dummy") == meta
        assert registry.get_instance("dummy") is tool

    def test_all_names(self):
        registry = ToolRegistry()
        registry.register(DUMMY_META, DummyTool())
        assert "dummy" in registry.all_names()

    def test_unregister(self):
        registry = ToolRegistry()
        tool = DummyTool()
        registry.register(DUMMY_META, tool)
        assert registry.size == 1

        registry.unregister("dummy")
        assert registry.size == 0
        assert registry.get_metadata("dummy") is None

    def test_extensibility_11th_tool(self):
        """Adding an 11th tool should not break anything."""
        registry = ToolRegistry()

        # Register 10 dummy tools
        for i in range(10):
            meta = ToolMetadata(
                name=f"tool_{i}",
                display_name=f"Tool {i}",
                description=f"Tool number {i}",
            )

            class TempTool(DynamicTool):
                name: str = f"tool_{i}"
                description: str = f"Tool {i}"

                def _run(self, **kwargs) -> str:
                    return f"result {i}"

            registry.register(meta, TempTool())

        assert registry.size == 10

        # Add 11th tool
        meta_11 = ToolMetadata(
            name="tool_10",
            display_name="Tool 10",
            description="The 11th tool",
        )

        class Tool11(DynamicTool):
            name: str = "tool_10"
            description: str = "Tool 10"

            def _run(self) -> str:
                return "result 10"

        registry.register(meta_11, Tool11())
        assert registry.size == 11
        assert registry.get_metadata("tool_10") is not None
