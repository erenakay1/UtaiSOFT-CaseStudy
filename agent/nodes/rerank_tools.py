"""Node: rerank_tools — Cross-encoder reranking."""

from __future__ import annotations

from agent.state import AgentState
from search.reranker import rerank_tools as rerank


def rerank_tools(state: AgentState) -> dict:
    """Re-score candidates using a cross-encoder model."""
    query = state.get("analyzed_intent", state["user_query"])
    candidates = state.get("candidate_tools", [])

    reranked = rerank(query, candidates)

    return {"reranked_tools": reranked}
