"""
Tool loader — registers all 10 tools into the registry.

Import this module and call ``load_all_tools()`` to get a fully populated
ToolRegistry that can be passed to the agent graph.
"""

from __future__ import annotations

from registry.registry import ToolRegistry

from tools.weather import WeatherTool
from tools.web_search import WebSearchTool
from tools.currency import CurrencyTool
from tools.translate import TranslateTool
from tools.calendar_tool import CalendarTool
from tools.email_tool import EmailTool
from tools.document_reader import DocumentReaderTool
from tools.database import DatabaseTool
from tools.code_executor import CodeExecutorTool
from tools.timer import TimerTool
from tools.ip_lookup import IPLookupTool

# All tool classes — add new tools to this list to register them
ALL_TOOL_CLASSES = [
    WeatherTool,
    WebSearchTool,
    CurrencyTool,
    TranslateTool,
    CalendarTool,
    EmailTool,
    DocumentReaderTool,
    DatabaseTool,
    CodeExecutorTool,
    TimerTool,
    IPLookupTool,
]


def load_all_tools() -> ToolRegistry:
    """Instantiate every tool and register it.

    Returns a ready-to-use ``ToolRegistry``.
    """
    registry = ToolRegistry()

    from tools.metadata import get_tool_metadata

    for tool_cls in ALL_TOOL_CLASSES:
        instance = tool_cls()
        metadata = get_tool_metadata(instance.name)
        registry.register(metadata, instance)

    return registry
