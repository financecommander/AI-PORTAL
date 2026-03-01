"""Pipeline registry — hand-coded pipelines + Orchestra auto-discovery.

Hand-coded pipelines (Lex, Calculus, Forge) are registered explicitly.
Any .orca YAML files in backend/pipelines/definitions/ are discovered
and registered automatically at startup. Drop a file, restart, done.

Hand-coded pipelines take priority on name collisions.
"""

import logging
from backend.pipelines.base_pipeline import BasePipeline
from backend.pipelines.forge_intelligence import ForgeIntelligence
from backend.pipelines.lead_ranking_pipeline import LeadRankingPipeline
from backend.pipelines.underwriting_pipeline import UnderwritingPipeline
from backend.pipelines.due_diligence_pipeline import DueDiligencePipeline
from backend.pipelines.portfolio_monitoring_pipeline import PortfolioMonitoringPipeline
from backend.pipelines.investor_reporting_pipeline import InvestorReportingPipeline
from backend.pipelines.skiptrace_pipeline import SkipTracePipeline

logger = logging.getLogger(__name__)


def _create_lex():
    from backend.pipelines.lex_intelligence import create_lex_intelligence
    return create_lex_intelligence()


def _create_calculus():
    from backend.pipelines.calculus_intelligence import create_calculus_intelligence
    return create_calculus_intelligence()


# Hand-coded pipeline factories (always available)
_REGISTRY: dict[str, callable] = {
    "lex_intelligence": _create_lex,
    "calculus_intelligence": _create_calculus,
    "forge_intelligence": lambda: ForgeIntelligence(),
    "lead_ranking": lambda: LeadRankingPipeline(),
    "underwriting": lambda: UnderwritingPipeline(),
    "due_diligence": lambda: DueDiligencePipeline(),
    "portfolio_monitoring": lambda: PortfolioMonitoringPipeline(),
    "investor_reporting": lambda: InvestorReportingPipeline(),
    "skiptrace": lambda: SkipTracePipeline(),
}

_INSTANCES: dict[str, BasePipeline] = {}
_ORCHESTRA_LOADED: bool = False


def _load_orchestra_pipelines():
    """Discover and register .orca pipeline definitions.

    Called once on first access. Failures are logged but don't crash.
    """
    global _ORCHESTRA_LOADED
    if _ORCHESTRA_LOADED:
        return
    _ORCHESTRA_LOADED = True

    try:
        from backend.pipelines.orch_loader import discover_orca_pipelines

        orca_pipelines = discover_orca_pipelines()
        for name, pipeline in orca_pipelines.items():
            if name in _REGISTRY:
                logger.info(
                    f"Orchestra: skipping '{name}' — "
                    f"hand-coded pipeline takes priority"
                )
                continue
            # Register as a pre-built instance (not a factory)
            _INSTANCES[name] = pipeline
            # Add a dummy factory so list_pipelines sees it
            _REGISTRY[name] = lambda n=name: _INSTANCES[n]
            logger.info(f"Orchestra: registered '{name}' from .orca definition")

    except ImportError as e:
        logger.warning(f"Orchestra loader not available: {e}")
    except Exception as e:
        logger.error(f"Orchestra discovery failed: {e}", exc_info=True)


def get_pipeline(name: str) -> BasePipeline:
    """Get a pipeline instance by name.

    Args:

    Returns:
        Pipeline instance

    Raises:
        KeyError: If pipeline not found
    """
    # Ensure Orchestra pipelines are loaded
    _load_orchestra_pipelines()

    if name not in _INSTANCES:
        if name not in _REGISTRY:
            raise KeyError(
                f"Pipeline '{name}' not registered. "
                f"Available: {list(_REGISTRY.keys())}"
            )
        _INSTANCES[name] = _REGISTRY[name]()
    return _INSTANCES[name]


def list_pipelines() -> list[dict]:
    """List all available pipelines (hand-coded + Orchestra).

    Returns:
        List of pipeline metadata dictionaries.
    """
    # Ensure Orchestra pipelines are loaded
    _load_orchestra_pipelines()

    result = []
    for name in _REGISTRY:
        try:
            pipeline = get_pipeline(name)
            result.append({
                "name": name,
                "display_name": pipeline.name,
                "description": pipeline.description,
                "agents": pipeline.get_agents(),
                "type": "multi_agent" if len(pipeline.get_agents()) > 1 else "single",
            })
        except Exception as e:
            logger.error(f"Failed to load pipeline '{name}': {e}")
            continue

    return result
