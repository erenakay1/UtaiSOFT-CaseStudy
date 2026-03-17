"""Base tool class — all 10 tools extend this."""

from __future__ import annotations

from langchain_core.tools import BaseTool

from registry.models import ToolMetadata


class DynamicTool(BaseTool):
    """Base class. Metadata is now provided via an external dictionary to avoid Pydantic metaclass conflicts."""
    pass
