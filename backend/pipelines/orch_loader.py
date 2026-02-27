"""Orchestra Loader — discovers and registers .orca pipeline definitions.

Scans a definitions directory for .orca YAML files, parses each one,
and builds CrewPipeline instances that can be registered in the pipeline
registry alongside hand-coded pipelines.

Usage:
    from backend.pipelines.orch_loader import discover_orca_pipelines

    pipelines = discover_orca_pipelines()
    # Returns: {"pipeline-name": CrewPipeline, ...}
"""

import os
import logging
from pathlib import Path
from typing import Optional

import yaml

from backend.pipelines.orch_pipeline import build_pipeline_from_config
from backend.pipelines.crew_pipeline import CrewPipeline

logger = logging.getLogger(__name__)

# Default location for .orca definitions
DEFAULT_DEFINITIONS_DIR = os.path.join(
    os.path.dirname(__file__), "definitions"
)


def load_orca_file(filepath: str) -> dict:
    """Load and parse a single .orca YAML file.

    Args:
        filepath: Path to the .orca file.

    Returns:
        Parsed YAML as dict.

    Raises:
        FileNotFoundError: If file doesn't exist.
        yaml.YAMLError: If YAML is malformed.
    """
    with open(filepath, "r") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        raise ValueError(f"{filepath} did not parse to a dict")

    return config


def build_from_file(filepath: str) -> CrewPipeline:
    """Load an .orca file and build a CrewPipeline from it.

    Args:
        filepath: Path to the .orca file.

    Returns:
        Configured CrewPipeline instance.
    """
    config = load_orca_file(filepath)

    # Inject source file path into config for debugging
    config.setdefault("_source", filepath)

    pipeline = build_pipeline_from_config(config)

    logger.info(f"Orchestra: loaded pipeline '{pipeline.name}' from {filepath}")
    return pipeline


def discover_orca_pipelines(
    definitions_dir: Optional[str] = None,
) -> dict[str, CrewPipeline]:
    """Scan a directory for .orca files and build all pipelines.

    Args:
        definitions_dir: Directory to scan. Defaults to
            backend/pipelines/definitions/

    Returns:
        Dict mapping registry name -> CrewPipeline instance.
        Registry name is derived from the filename:
            calculus_reasoning.orca -> "calculus_reasoning"
    """
    scan_dir = definitions_dir or DEFAULT_DEFINITIONS_DIR

    if not os.path.isdir(scan_dir):
        logger.info(f"Orchestra: no definitions directory at {scan_dir}, skipping")
        return {}

    pipelines: dict[str, CrewPipeline] = {}
    orca_files = sorted(Path(scan_dir).glob("*.orca"))

    if not orca_files:
        logger.info(f"Orchestra: no .orca files found in {scan_dir}")
        return {}

    for filepath in orca_files:
        registry_name = filepath.stem  # filename without extension
        try:
            pipeline = build_from_file(str(filepath))
            pipelines[registry_name] = pipeline
            logger.info(
                f"Orchestra: registered '{registry_name}' "
                f"({len(pipeline.agents)} agents)"
            )
        except Exception as e:
            logger.error(
                f"Orchestra: failed to load {filepath.name}: {e}",
                exc_info=True,
            )
            # Don't crash the whole registry for one bad file
            continue

    logger.info(
        f"Orchestra: discovered {len(pipelines)} pipeline(s) "
        f"from {scan_dir}"
    )
    return pipelines