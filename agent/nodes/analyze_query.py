"""Node: analyze_query — Understand user intent via LLM."""

from __future__ import annotations

from langchain_openai import ChatOpenAI

import config
from agent.state import AgentState

_SYSTEM_PROMPT = """\
You are a query analyzer. Given a user query, extract the core intent in a clear, 
concise English sentence suitable for semantic search over tool descriptions.
Focus on WHAT the user wants to accomplish, not HOW.
Return ONLY the intent sentence, nothing else."""


def analyze_query(state: AgentState) -> dict:
    """Analyze the user query and extract intent for semantic search."""
    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.OPENAI_API_KEY,
        temperature=0,
    )

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": state["user_query"]},
    ]

    response = llm.invoke(messages)
    intent = response.content.strip()

    return {"analyzed_intent": intent}
