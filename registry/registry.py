"""
Tool Registry — central catalog of all available tools.

Tools register themselves here.  The registry holds metadata only;
actual tool *instances* (LangChain BaseTool subclasses) are resolved
lazily so that adding a new tool never touches orchestration code.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from langchain_core.tools import BaseTool

from registry.models import ToolMetadata

if TYPE_CHECKING:
    pass


class ToolRegistry:
    """In-memory registry that maps tool names → metadata + instances."""

    def __init__(self) -> None:
        self._metadata: dict[str, ToolMetadata] = {}
        self._instances: dict[str, BaseTool] = {}

    # ── Registration ───────────────────────────────────────────────────
    def register(self, metadata: ToolMetadata, instance: BaseTool) -> None:
        """Register a tool with its metadata and LangChain instance."""
        self._metadata[metadata.name] = metadata
        self._instances[metadata.name] = instance

    # ── Lookup ─────────────────────────────────────────────────────────
    def get_metadata(self, name: str) -> Optional[ToolMetadata]:
        return self._metadata.get(name)

    def get_instance(self, name: str) -> Optional[BaseTool]:
        return self._instances.get(name)

    def all_metadata(self) -> list[ToolMetadata]:
        return list(self._metadata.values())

    def all_names(self) -> list[str]:
        return list(self._metadata.keys())

    @property
    def size(self) -> int:
        return len(self._metadata)

    # ── Extensibility helper ───────────────────────────────────────────
    def unregister(self, name: str) -> None:
        self._metadata.pop(name, None)
        self._instances.pop(name, None)
