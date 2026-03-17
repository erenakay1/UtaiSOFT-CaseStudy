"""Pinecone vector search client."""

from __future__ import annotations

from pinecone import Pinecone

import config


_index = None


def _get_index():
    global _index
    if _index is None:
        pc = Pinecone(api_key=config.PINECONE_API_KEY)
        _index = pc.Index(config.PINECONE_INDEX_NAME)
    return _index


def search_tools(query_embedding: list[float], top_k: int | None = None) -> list[dict]:
    """Query Pinecone and return top-k matches.

    Each item in the returned list has keys:
        - name (str)
        - display_name (str)
        - description (str)
        - category (str)
        - score (float)  — cosine similarity
    """
    top_k = top_k or config.SEMANTIC_SEARCH_TOP_K
    index = _get_index()

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
    )

    candidates = []
    for match in results.get("matches", []):
        meta = match.get("metadata", {})
        candidates.append(
            {
                "name": meta.get("name", match["id"]),
                "display_name": meta.get("display_name", ""),
                "description": meta.get("description", ""),
                "category": meta.get("category", ""),
                "examples": meta.get("examples", ""),
                "score": match["score"],
            }
        )

    return candidates
