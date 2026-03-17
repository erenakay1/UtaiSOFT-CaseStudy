"""Node: synthesize — Turn tool output into a user-friendly response."""

from __future__ import annotations

from langchain_openai import ChatOpenAI

import config
from agent.state import AgentState

_SYSTEM_PROMPT = """\
You are a helpful assistant that presents tool results to the user.
Given the user's original question and the tool output, create a clear, 
natural, and helpful response in the same language the user used.
Do NOT make up information — only present what the tool returned.
If the tool returned an error, explain it helpfully."""


def synthesize(state: AgentState) -> dict:
    """Format the tool result into a natural-language response."""
    query = state["user_query"]
    tool_name = state.get("selected_tool", "unknown")
    tool_result = state.get("tool_result", "")

    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.OPENAI_API_KEY,
        temperature=0.3,
    )

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"User Question: {query}\n\n"
                f"Tool Used: {tool_name}\n\n"
                f"Tool Output:\n{tool_result}\n\n"
                f"Please provide a helpful response."
            ),
        },
    ]

    response = llm.invoke(messages)
    return {"final_response": response.content.strip()}


def no_tool_found(state: AgentState) -> dict:
    """Handle the case where no suitable tool was found."""
    query = state["user_query"]
    confidence = state.get("confidence", 0)

    return {
        "final_response": (
            f"Üzgünüm, '{query}' sorunuz için uygun bir araç bulunamadı.\n"
            f"(Güven skoru: {confidence:.2f})\n\n"
            f"Mevcut yeteneklerim:\n"
            f"  🌤 Hava durumu sorgulama\n"
            f"  🔍 Web araması\n"
            f"  💱 Döviz çevirme\n"
            f"  🌐 Dil çevirisi\n"
            f"  📅 Takvim yönetimi\n"
            f"  ✉️ E-posta gönderme/okuma\n"
            f"  📄 Belge okuma (PDF/TXT)\n"
            f"  🗄 Veritabanı sorgusu\n"
            f"  💻 Python kod çalıştırma\n"
            f"  ⏱ Timer/Alarm kurma"
        )
    }
