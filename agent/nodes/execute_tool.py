"""Node: execute_tool — Runs the selected tool with extracted params."""

from __future__ import annotations

from agent.state import AgentState
from registry.registry import ToolRegistry


# The registry is injected at graph-build time (see graph.py)
_registry: ToolRegistry | None = None


def set_registry(registry: ToolRegistry) -> None:
    """Called once at startup to inject the active registry."""
    global _registry
    _registry = registry


def execute_tool(state: AgentState) -> dict:
    """Invoke the selected tool and capture the result."""
    tool_name = state.get("selected_tool")
    params = state.get("tool_params", {})

    if not tool_name or _registry is None:
        return {"tool_result": "Tool bulunamadı veya seçilemedi."}

    instance = _registry.get_instance(tool_name)
    if instance is None:
        return {"tool_result": f"'{tool_name}' tool'u registry'de bulunamadı."}

    try:
        result = instance.invoke(params)
        return {"tool_result": str(result)}
    except Exception as e:
        return {"tool_result": f"Tool çalıştırma hatası ({tool_name}): {e}"}
