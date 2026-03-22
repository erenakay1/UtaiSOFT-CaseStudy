"""Node: analyze_query — Understand user intent via LLM."""

from __future__ import annotations

import functools
from langchain_openai import ChatOpenAI

import config
from agent.state import AgentState

_SYSTEM_PROMPT = """\
You are a query analyzer. Given a user query, extract the core intent in a clear, 
concise sentence suitable for semantic search over tool descriptions.
CRITICAL: You MUST write the intent in the EXACT SAME LANGUAGE as the user's original query. Do not translate it.
Focus on WHAT the user wants to accomplish, not HOW.
Return ONLY the intent sentence, nothing else."""

@functools.lru_cache(maxsize=1024)
def _get_intent_cached(query: str) -> str:
    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.OPENAI_API_KEY,
        temperature=0,
    )
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]
    response = llm.invoke(messages)
    return response.content.strip()


def analyze_query(state: AgentState) -> dict:
    """Analyze the user query and extract intent for semantic search."""
    intent = _get_intent_cached(state["user_query"])
    return {"analyzed_intent": intent}
