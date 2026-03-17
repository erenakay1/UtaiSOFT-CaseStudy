"""Node: search_tools — Semantic search via Pinecone."""

from __future__ import annotations

from agent.state import AgentState
from search.embedder import get_embedding
from search.pinecone_client import search_tools as pinecone_search


def search_tools(state: AgentState) -> dict:
    """Embed the analyzed intent and query Pinecone for candidate tools."""
    intent = state.get("analyzed_intent", state["user_query"])
    embedding = get_embedding(intent)
    candidates = pinecone_search(embedding)

    return {"candidate_tools": candidates}
