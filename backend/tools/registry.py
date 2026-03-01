"""Central registry mapping specialist IDs to lists of BaseTool instances."""

from backend.tools.base import BaseTool

_registry: dict[str, list[BaseTool]] = {}


def register_tools(specialist_id: str, tools: list[BaseTool]) -> None:
    """Register tools for a specialist."""
    _registry[specialist_id] = tools


def get_tools(specialist_id: str) -> list[BaseTool]:
    """Retrieve tools for a specialist (empty list if none registered)."""
    return _registry.get(specialist_id, [])


def has_tools(specialist_id: str) -> bool:
    """Check if a specialist has any registered tools."""
    return bool(_registry.get(specialist_id))


def list_all() -> dict[str, list[str]]:
    """Return a summary of all registered tools keyed by specialist ID."""
    return {sid: [t.name for t in tools] for sid, tools in _registry.items()}
