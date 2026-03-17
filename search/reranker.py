"""Cross-encoder reranker — filters and re-scores tool candidates."""

from __future__ import annotations

from sentence_transformers import CrossEncoder

import config

_model: CrossEncoder | None = None


def _get_model() -> CrossEncoder:
    global _model
    if _model is None:
        _model = CrossEncoder(config.RERANKER_MODEL)
    return _model


def rerank_tools(
    query: str,
    candidates: list[dict],
    threshold: float | None = None,
) -> list[dict]:
    """Re-score *candidates* against *query* using a cross-encoder.

    Returns only candidates whose cross-encoder score ≥ threshold,
    sorted descending by score.  Each dict gets an extra key
    ``rerank_score``.
    """
    if not candidates:
        return []

    threshold = threshold if threshold is not None else config.RERANKER_THRESHOLD
    model = _get_model()

    pairs = [
        (query, f"{c.get('description', '')} {c.get('examples', '')}")
        for c in candidates
    ]
    scores = model.predict(pairs)

    import math
    
    scored = []
    for candidate, score in zip(candidates, scores):
        prob = 1 / (1 + math.exp(-float(score)))
        if prob >= threshold:
            candidate["rerank_score"] = float(prob)
            scored.append(candidate)

    scored.sort(key=lambda c: c["rerank_score"], reverse=True)
    return scored
