"""
Script: index_tools — upserts tool embeddings into Pinecone.

Usage:
    python scripts/index_tools.py
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console

from tools.loader import load_all_tools
from registry.indexer import index_tools

console = Console()


def main():
    console.print("\n[bold cyan]🔧 Dynamic Tool Selection — Pinecone Indexer[/bold cyan]\n")

    # 1. Load all tools
    console.print("[yellow]Loading tools...[/yellow]")
    registry = load_all_tools()
    console.print(f"  ✅ {registry.size} tools loaded\n")

    # 2. List them
    for meta in registry.all_metadata():
        console.print(f"  • [green]{meta.name}[/green] — {meta.display_name}")
    console.print()

    # 3. Index into Pinecone
    console.print("[yellow]Indexing into Pinecone...[/yellow]")
    count = index_tools(registry)
    console.print(f"  ✅ {count} vectors upserted\n")

    console.print("[bold green]Done![/bold green]\n")


if __name__ == "__main__":
    main()
