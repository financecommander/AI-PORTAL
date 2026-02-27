"""Orchestra Pipeline — builds CrewAI pipelines from declarative YAML definitions.

This is the core of the Orchestra DSL integration. It reads .orca YAML files
and dynamically constructs CrewPipeline instances with proper LLM routing,
agent definitions, task chains, and optional quality gates.

A pipeline definition looks like:

    pipeline:
      name: My Pipeline
      description: What it does
      verbose: true

    agents:
      researcher:
        role: Lead Researcher
        goal: Find relevant information
        backstory: You are an expert researcher...
        model: gpt-4o
        temperature: 0.3

    tasks:
      - agent: researcher
        description: Research the user's query
        expected_output: A detailed research memo

    gates:  # optional
      - name: confidence_check
        after_task: 3
        min_confidence: 0.7
        on_fail: log_warning
"""

import logging
from typing import Any, Optional
from crewai import Agent, Task, LLM
from backend.pipelines.crew_pipeline import CrewPipeline
from backend.config.settings import settings

logger = logging.getLogger(__name__)

# Model prefix -> API key mapping
_MODEL_KEY_MAP = {
    "gpt-": "openai",
    "o1": "openai",
    "o3": "openai",
    "xai/": "xai",
    "grok": "xai",
    "gemini/": "google",
    "gemini": "google",
    "anthropic/": "anthropic",
    "claude": "anthropic",
}


def _resolve_api_key(model: str) -> str:
    """Resolve the API key for a given model string."""
    model_lower = model.lower()
    for prefix, provider in _MODEL_KEY_MAP.items():
        if model_lower.startswith(prefix):
            key_map = {
                "openai": settings.openai_api_key,
                "xai": settings.xai_api_key,
                "google": settings.google_api_key,
                "anthropic": settings.anthropic_api_key,
            }
            return key_map.get(provider, "") or "dummy"
    # Default to OpenAI
    return settings.openai_api_key or "dummy"


def _needs_native_bypass(model: str) -> bool:
    """Check if model needs use_native=False for LiteLLM routing."""
    model_lower = model.lower()
    return (
        model_lower.startswith("gemini/")
        or model_lower.startswith("gemini")
        or model_lower.startswith("xai/")
        or model_lower.startswith("grok")
    )


def build_llm(model: str, temperature: float = 0.4) -> LLM:
    """Build a crewai.LLM instance from a model string.

    All LLMs use crewai.LLM (not langchain wrappers) so LiteLLM
    tracks tokens automatically.
    """
    kwargs: dict[str, Any] = {
        "model": model,
        "api_key": _resolve_api_key(model),
        "temperature": temperature,
    }
    if _needs_native_bypass(model):
        kwargs["use_native"] = False
    return LLM(**kwargs)


def build_pipeline_from_config(config: dict) -> CrewPipeline:
    """Build a CrewPipeline from a parsed YAML/dict configuration.

    Args:
        config: Parsed .orca YAML as a dict.

    Returns:
        A fully configured CrewPipeline ready for registration.

    Raises:
        ValueError: If the configuration is invalid.
    """
    # --- Validate top-level structure ---
    pipeline_cfg = config.get("pipeline", {})
    name = pipeline_cfg.get("name")
    if not name:
        raise ValueError("Pipeline config must have pipeline.name")

    description = pipeline_cfg.get("description", "")
    verbose = pipeline_cfg.get("verbose", True)

    agents_cfg = config.get("agents", {})
    tasks_cfg = config.get("tasks", [])

    if not agents_cfg:
        raise ValueError(f"Pipeline '{name}' has no agents defined")
    if not tasks_cfg:
        raise ValueError(f"Pipeline '{name}' has no tasks defined")

    # --- Build LLM instances (deduplicated by model+temperature) ---
    llm_cache: dict[str, LLM] = {}

    def get_llm(model: str, temperature: float = 0.4) -> LLM:
        cache_key = f"{model}:{temperature}"
        if cache_key not in llm_cache:
            llm_cache[cache_key] = build_llm(model, temperature)
        return llm_cache[cache_key]

    # --- Build Agent instances ---
    agent_map: dict[str, Agent] = {}
    agent_order: list[str] = []

    for agent_key, agent_cfg in agents_cfg.items():
        role = agent_cfg.get("role", agent_key)
        goal = agent_cfg.get("goal", f"Complete tasks as {role}")
        backstory = agent_cfg.get("backstory", f"You are a {role}.")
        model = agent_cfg.get("model", "gpt-4o")
        temperature = agent_cfg.get("temperature", 0.4)
        allow_delegation = agent_cfg.get("allow_delegation", False)

        agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=get_llm(model, temperature),
            verbose=verbose,
            allow_delegation=allow_delegation,
        )
        agent_map[agent_key] = agent
        agent_order.append(agent_key)

    # --- Build Task instances ---
    tasks: list[Task] = []

    for i, task_cfg in enumerate(tasks_cfg):
        agent_key = task_cfg.get("agent")
        if not agent_key or agent_key not in agent_map:
            available = list(agent_map.keys())
            raise ValueError(
                f"Task {i + 1} references agent '{agent_key}' "
                f"which is not defined. Available: {available}"
            )

        description = task_cfg.get("description", "")
        expected_output = task_cfg.get("expected_output", "Complete the task.")

        task = Task(
            description=description,
            expected_output=expected_output,
            agent=agent_map[agent_key],
        )
        tasks.append(task)

    # --- Build ordered agent list (task order determines agent order) ---
    seen: set[str] = set()
    ordered_agents: list[Agent] = []
    for task_cfg in tasks_cfg:
        agent_key = task_cfg.get("agent")
        if agent_key and agent_key not in seen:
            ordered_agents.append(agent_map[agent_key])
            seen.add(agent_key)

    # --- Parse quality gates (stored as metadata, enforced at execution) ---
    gates = config.get("gates", [])
    gate_metadata = []
    for gate in gates:
        gate_metadata.append({
            "name": gate.get("name", "unnamed_gate"),
            "after_task": gate.get("after_task"),
            "after_agent": gate.get("after"),
            "min_confidence": gate.get("min_confidence"),
            "rule": gate.get("rule"),
            "on_fail": gate.get("on_fail", "log_warning"),
        })

    logger.info(
        f"Orchestra: built pipeline '{name}' with {len(ordered_agents)} agents, "
        f"{len(tasks)} tasks, {len(gate_metadata)} gates"
    )

    pipeline = CrewPipeline(
        name=name,
        description=description,
        agents=ordered_agents,
        tasks=tasks,
        verbose=verbose,
    )

    # Attach gate metadata for future enforcement
    pipeline._orchestra_gates = gate_metadata
    pipeline._orchestra_config = config

    return pipeline