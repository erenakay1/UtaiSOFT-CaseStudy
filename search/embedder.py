"""Text → embedding via OpenAI."""

from __future__ import annotations

from openai import OpenAI

import config

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _client


def get_embedding(text: str) -> list[float]:
    """Return an embedding vector for *text* using the configured model."""
    client = _get_client()
    response = client.embeddings.create(
        input=text,
        model=config.EMBEDDING_MODEL,
    )
    return response.data[0].embedding
