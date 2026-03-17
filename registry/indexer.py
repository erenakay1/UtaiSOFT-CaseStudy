"""
Pinecone Indexer — upserts tool embeddings into Pinecone.

Run this once (or whenever tools change) via:
    python scripts/index_tools.py
"""

from __future__ import annotations

from pinecone import Pinecone, ServerlessSpec

import config
from registry.registry import ToolRegistry
from search.embedder import get_embedding


def ensure_index_exists(pc: Pinecone) -> None:
    """Create the Pinecone index if it doesn't already exist."""
    existing = [idx.name for idx in pc.list_indexes()]
    if config.PINECONE_INDEX_NAME not in existing:
        pc.create_index(
            name=config.PINECONE_INDEX_NAME,
            dimension=config.EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )


def index_tools(registry: ToolRegistry) -> int:
    """Embed every tool's metadata and upsert into Pinecone.

    Returns the number of vectors upserted.
    """
    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    ensure_index_exists(pc)
    index = pc.Index(config.PINECONE_INDEX_NAME)

    vectors: list[dict] = []
    for meta in registry.all_metadata():
        embedding = get_embedding(meta.embedding_text)
        vectors.append(
            {
                "id": meta.name,
                "values": embedding,
                "metadata": {
                    "name": meta.name,
                    "display_name": meta.display_name,
                    "description": meta.description,
                    "category": meta.category,
                    "examples": " | ".join(meta.examples),
                },
            }
        )

    if vectors:
        index.upsert(vectors=vectors)

    return len(vectors)
