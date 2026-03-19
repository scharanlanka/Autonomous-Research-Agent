from typing import Any, Literal
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    tool: str
    query: str
    results: list[dict[str, Any]] = Field(default_factory=list)

class SourceItem(BaseModel):
    title: str
    url: str
    snippet: str | None = None
    accessed_at: float | None = None

class ResearchState(BaseModel):
    query: str
    status: Literal["running", "done", "error"] = "running"
    created_at: float

    plan: list[str] = Field(default_factory=list)
    tool_results: list[ToolResult] = Field(default_factory=list)
    sources: list[SourceItem] = Field(default_factory=list)

    memory_context: list[str] = Field(default_factory=list)

    draft_report: str = ""
    final_report: str = ""

    logs: list[str] = Field(default_factory=list)