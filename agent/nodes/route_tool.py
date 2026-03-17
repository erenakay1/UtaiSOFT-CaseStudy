"""Node: route_tool — LLM-based final tool selection + parameter extraction."""

from __future__ import annotations

import json

from langchain_openai import ChatOpenAI

import config
from agent.state import AgentState

_SYSTEM_PROMPT = """\
You are a tool routing assistant.
The user has a goal. You have a set of available tools.
Select the SINGLE BEST tool to accomplish the user's intent.
If no tool is appropriate, DO NOT call any tools. Just respond normally.
"""


def route_tool(state: AgentState) -> dict:
    """Use OpenAI Function Calling to select the best tool and extract parameters."""
    query = state["user_query"]
    reranked = state.get("reranked_tools", [])

    if not reranked:
        return {
            "selected_tool": None,
            "tool_params": {},
            "confidence": 0.0,
        }

    from tools.metadata import get_tool_metadata
    
    # Build OpenAI Tool schemas dynamically from registry metadata
    tools_for_llm = []
    for t in reranked:
        try:
            meta = get_tool_metadata(t["name"])
            tool_params = meta.parameters
        except ValueError:
            tool_params = t.get("parameters", {})
            
        tools_for_llm.append({
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": {
                    "type": "object",
                    "properties": tool_params,
                    "required": list(tool_params.keys()),
                }
            }
        })

    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.OPENAI_API_KEY,
        temperature=0,
    ).bind_tools(tools_for_llm)

    import datetime
    
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Current Date/Time: {datetime.datetime.now().isoformat()}\n\n"
                f"User Query: {query}"
            ),
        },
    ]

    response = llm.invoke(messages)
    
    # Check if the LLM called a tool
    if getattr(response, "tool_calls", None) and len(response.tool_calls) > 0:
        tool_call = response.tool_calls[0]
        selected = tool_call["name"]
        params = tool_call["args"]
        # With OpenAI tool calling, if it chooses a tool, confidence is effectively 1.0
        confidence = 1.0
    else:
        selected = None
        params = {}
        confidence = 0.0

    return {
        "selected_tool": selected,
        "tool_params": params,
        "confidence": confidence,
    }
