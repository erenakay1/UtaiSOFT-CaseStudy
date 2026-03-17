"""
LangGraph state machine — the heart of the Dynamic Tool Selection Agent.

Graph:
  analyze_query → search_tools → rerank_tools → route_tool
    ├─ (tool found) → execute_tool → synthesize → END
    └─ (no tool)   → no_tool_found → END
"""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from agent.state import AgentState
from agent.nodes.analyze_query import analyze_query
from agent.nodes.search_tools import search_tools
from agent.nodes.rerank_tools import rerank_tools
from agent.nodes.route_tool import route_tool
from agent.nodes.execute_tool import execute_tool, set_registry
from agent.nodes.synthesize import synthesize, no_tool_found
from registry.registry import ToolRegistry


def _should_execute(state: AgentState) -> str:
    """Conditional edge: decide whether to execute a tool or fall back."""
    if state.get("selected_tool"):
        return "execute_tool"
    return "no_tool_found"


def build_graph(registry: ToolRegistry) -> StateGraph:
    """Construct the LangGraph agent graph.

    The *registry* is injected so the execute_tool node can look up
    tool instances at runtime.
    """
    # Inject registry into the execute node
    set_registry(registry)

    graph = StateGraph(AgentState)

    # ── Add nodes ──────────────────────────────────────────────────────
    graph.add_node("analyze_query", analyze_query)
    graph.add_node("search_tools", search_tools)
    graph.add_node("rerank_tools", rerank_tools)
    graph.add_node("route_tool", route_tool)
    graph.add_node("execute_tool", execute_tool)
    graph.add_node("synthesize", synthesize)
    graph.add_node("no_tool_found", no_tool_found)

    # ── Define edges ───────────────────────────────────────────────────
    graph.set_entry_point("analyze_query")

    graph.add_edge("analyze_query", "search_tools")
    graph.add_edge("search_tools", "rerank_tools")
    graph.add_edge("rerank_tools", "route_tool")

    # Conditional branch after routing
    graph.add_conditional_edges(
        "route_tool",
        _should_execute,
        {
            "execute_tool": "execute_tool",
            "no_tool_found": "no_tool_found",
        },
    )

    graph.add_edge("execute_tool", "synthesize")
    graph.add_edge("synthesize", END)
    graph.add_edge("no_tool_found", END)

    return graph.compile()
