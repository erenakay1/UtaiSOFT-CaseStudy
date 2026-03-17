"""Agent state definition for LangGraph."""

from __future__ import annotations

from typing import Any, Optional

from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """State that flows through the LangGraph nodes."""

    # ── Input ──────────────────────────────────────────────────────────
    user_query: str

    # ── Query Analysis ─────────────────────────────────────────────────
    analyzed_intent: str

    # ── Tool Search ────────────────────────────────────────────────────
    candidate_tools: list[dict[str, Any]]       # from Pinecone
    reranked_tools: list[dict[str, Any]]         # after cross-encoder

    # ── Tool Routing ───────────────────────────────────────────────────
    selected_tool: Optional[str]
    tool_params: Optional[dict[str, Any]]
    confidence: float

    # ── Execution ──────────────────────────────────────────────────────
    tool_result: Optional[str]

    # ── Output ─────────────────────────────────────────────────────────
    final_response: Optional[str]
