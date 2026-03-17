"""Pydantic models for tool metadata."""

from pydantic import BaseModel, Field


class ToolMetadata(BaseModel):
    """Metadata describing a tool in the registry."""

    name: str = Field(..., description="Unique tool identifier (snake_case)")
    display_name: str = Field(..., description="Human-readable tool name")
    description: str = Field(
        ...,
        description="Detailed description of what the tool does. "
        "Used for semantic search embedding.",
    )
    parameters: dict = Field(
        default_factory=dict,
        description="JSON-Schema style parameter definitions",
    )
    category: str = Field(
        default="general",
        description="Tool category (information, communication, utility, computation)",
    )
    examples: list[str] = Field(
        default_factory=list,
        description="Example user queries that should trigger this tool",
    )

    @property
    def embedding_text(self) -> str:
        """Combine description + examples into a single string for embedding."""
        parts = [self.description]
        if self.examples:
            parts.append("Example queries: " + " | ".join(self.examples))
        return " ".join(parts)
