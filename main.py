#!/usr/bin/env python3
"""
Dynamic Tool Selection System — Main Entry Point

A zero-knowledge agent that dynamically discovers and selects
the right tool for any user query using:
  1. Semantic Search (Pinecone)
  2. Cross-Encoder Reranking
  3. LLM-based Routing (GPT-4o-mini)

Usage:
    python main.py              # Interactive chat
    python main.py --index      # Index tools into Pinecone first
"""

from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def index_tools_command():
    """Index all tool metadata into Pinecone."""
    from tools.loader import load_all_tools
    from registry.indexer import index_tools

    console.print("\n[bold cyan]🔧 Indexing tools into Pinecone...[/bold cyan]\n")
    registry = load_all_tools()

    for meta in registry.all_metadata():
        console.print(f"  • [green]{meta.name}[/green] — {meta.display_name}")

    count = index_tools(registry)
    console.print(f"\n  ✅ {count} tool vectors upserted to Pinecone.\n")


def run_chat():
    """Start the interactive chat loop."""
    from tools.loader import load_all_tools
    from agent.graph import build_graph

    console.print(
        Panel(
            "[bold cyan]Dynamic Tool Selection Agent[/bold cyan]\n\n"
            "Zero-knowledge agent — tool'ları otomatik keşfeder.\n"
            "Çıkmak için [bold]quit[/bold] veya [bold]exit[/bold] yazın.",
            title="🤖 DTS Agent",
            border_style="cyan",
        )
    )

    # Load tools & build graph
    console.print("[dim]Loading tools...[/dim]")
    registry = load_all_tools()
    console.print(f"[dim]  → {registry.size} tools registered[/dim]")

    console.print("[dim]Building agent graph...[/dim]")
    graph = build_graph(registry)
    console.print("[dim]  → Ready![/dim]\n")

    while True:
        try:
            user_input = console.input("[bold green]You → [/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            console.print("[dim]Goodbye![/dim]")
            break

        # Run the agent pipeline
        console.print("[dim]Thinking...[/dim]")

        try:
            result = graph.invoke({"user_query": user_input})

            intent = result.get("analyzed_intent", "")
            selected = result.get("selected_tool", None)
            confidence = result.get("confidence", 0)
            params = result.get("tool_params", {})
            candidates = result.get("candidate_tools", [])
            reranked = result.get("reranked_tools", [])

            console.print(
                f"\n[dim]  📊 Intent: {intent}[/dim]\n"
                f"[dim]  🔍 Candidates: {[c['name'] for c in candidates]}[/dim]\n"
                f"[dim]  📈 Reranked: {[c['name'] for c in reranked]}[/dim]\n"
                f"[dim]  🎯 Selected: {selected} (confidence: {confidence:.2f})[/dim]\n"
                f"[dim]  ⚙️ Params:  {params}[/dim]\n"
            )

            response = result.get("final_response", "Yanıt oluşturulamadı.")
            console.print(Panel(Markdown(response), title="🤖 Agent", border_style="blue"))
            console.print()

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]\n")


def main():
    parser = argparse.ArgumentParser(description="Dynamic Tool Selection Agent")
    parser.add_argument(
        "--index",
        action="store_true",
        help="Index tool metadata into Pinecone (run once)",
    )
    args = parser.parse_args()

    if args.index:
        index_tools_command()
    else:
        run_chat()


if __name__ == "__main__":
    main()
