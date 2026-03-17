"""Node: route_tool — LLM-based final tool selection + parameter extraction."""

from __future__ import annotations

import json

from langchain_openai import ChatOpenAI

import config
from agent.state import AgentState

_SYSTEM_PROMPT = """\
You are a tool routing assistant. Based on the user query and available tools,
select THE SINGLE BEST tool to execute, and extract the required parameters.

Respond ONLY with valid JSON in this exact format:
{{
  "selected_tool": "<tool_name or null>",
  "confidence": <0.0 to 1.0>,
  "parameters": {{}},
  "reasoning": "<brief explanation>"
}}

Rules:
- If NO tool is appropriate, set selected_tool to null and confidence to 0.
- Extract parameter values directly from the user query when possible.
- For missing required parameters, use reasonable defaults or leave empty strings.
- Confidence should reflect how certain you are that this tool matches the intent."""


def route_tool(state: AgentState) -> dict:
    """Use LLM to select the best tool and extract parameters."""
    query = state["user_query"]
    reranked = state.get("reranked_tools", [])

    if not reranked:
        return {
            "selected_tool": None,
            "tool_params": {},
            "confidence": 0.0,
        }

    # Build tool descriptions for the LLM
    tool_descriptions = []
    for t in reranked:
        tool_descriptions.append(
            f"- {t['name']} ({t['display_name']}): {t['description']}"
        )
    tools_text = "\n".join(tool_descriptions)

    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.OPENAI_API_KEY,
        temperature=0,
    )

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"User Query: {query}\n\n"
                f"Available Tools:\n{tools_text}\n\n"
                f"Select the best tool and extract parameters."
            ),
        },
    ]

    response = llm.invoke(messages)
    content = response.content.strip()

    # Parse JSON response
    try:
        # Handle markdown code blocks
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        result = json.loads(content)
    except json.JSONDecodeError:
        return {
            "selected_tool": None,
            "tool_params": {},
            "confidence": 0.0,
        }

    selected = result.get("selected_tool")
    confidence = float(result.get("confidence", 0))
    params = result.get("parameters", {})

    # Apply confidence threshold
    if confidence < config.ROUTER_CONFIDENCE_THRESHOLD:
        selected = None
        params = {}

    return {
        "selected_tool": selected,
        "tool_params": params,
        "confidence": confidence,
    }
