"""Tests for the search pipeline (embedder, Pinecone, reranker).

NOTE: These tests require API keys to be configured in .env.
Tests marked with @pytest.mark.integration require live APIs.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


@pytest.mark.integration
class TestEmbedder:
    """Tests for the embedding function (requires OpenAI API key)."""

    def test_embedding_returns_list(self):
        from search.embedder import get_embedding

        embedding = get_embedding("test query")
        assert isinstance(embedding, list)
        assert len(embedding) > 0

    def test_embedding_dimension(self):
        from search.embedder import get_embedding
        import config

        embedding = get_embedding("hello world")
        assert len(embedding) == config.EMBEDDING_DIMENSION


@pytest.mark.integration
class TestReranker:
    """Tests for the cross-encoder reranker."""

    def test_rerank_filters_irrelevant(self):
        from search.reranker import rerank_tools

        candidates = [
            {"name": "weather", "description": "Get weather information for cities", "score": 0.8},
            {"name": "email", "description": "Send and read emails via Gmail", "score": 0.5},
        ]
        query = "What is the weather in Istanbul?"
        reranked = rerank_tools(query, candidates, threshold=0.0)
        # Weather should rank higher than email for this query
        assert len(reranked) > 0
        assert reranked[0]["name"] == "weather"

    def test_rerank_empty_candidates(self):
        from search.reranker import rerank_tools

        result = rerank_tools("test", [], threshold=0.0)
        assert result == []


@pytest.mark.integration
class TestPineconeSearch:
    """Tests for Pinecone vector search (requires Pinecone API key + indexed data)."""

    def test_search_returns_results(self):
        from search.embedder import get_embedding
        from search.pinecone_client import search_tools

        embedding = get_embedding("What is the weather?")
        results = search_tools(embedding, top_k=3)
        assert isinstance(results, list)
        assert len(results) <= 3
