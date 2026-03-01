"""Tools package — tool-calling infrastructure for AI Portal specialists."""

from backend.tools.base import BaseTool, ToolResult
from backend.tools.registry import register_tools, get_tools, has_tools


def register_all_tools() -> None:
    """Register all specialist→tool mappings.  Called once at app startup."""
    from backend.tools.skiptrace_tool import SkipTraceTool
    register_tools("skiptrace", [SkipTraceTool()])


__all__ = [
    "BaseTool",
    "ToolResult",
    "register_tools",
    "get_tools",
    "has_tools",
    "register_all_tools",
]
