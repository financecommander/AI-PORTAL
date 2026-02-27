"""Pipeline registry for managing available pipelines."""

from backend.pipelines.base_pipeline import BasePipeline
from backend.pipelines.lex_pipeline import create_lex_pipeline


_REGISTRY: dict[str, callable] = {
    "lex-intelligence": create_lex_pipeline,
}

_INSTANCES: dict[str, BasePipeline] = {}


def get_pipeline(name: str) -> BasePipeline:
    """
    Get a pipeline instance by name.
    
    Args:
        name: Pipeline name
    
    Returns:
        Pipeline instance
    
    Raises:
        KeyError: If pipeline not found
    """
    if name not in _INSTANCES:
        if name not in _REGISTRY:
            raise KeyError(
                f"Pipeline '{name}' not registered. "
                f"Available: {list(_REGISTRY.keys())}"
            )
        _INSTANCES[name] = _REGISTRY[name]()
    return _INSTANCES[name]


def list_pipelines() -> list[dict]:
    """
    List all available pipelines.
    
    Returns:
        List of pipeline metadata dictionaries
    """
    result = []
    for name in _REGISTRY:
        pipeline = get_pipeline(name)
        result.append({
            "name": name,
            "display_name": pipeline.name,
            "description": pipeline.description,
            "agents": pipeline.get_agents(),
            "type": "multi_agent" if len(pipeline.get_agents()) > 1 else "single",
        })
    return result
