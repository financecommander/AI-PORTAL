"""SkipTrace Tool — subprocess wrapper around skip-trace-scraper.

Writes a JSON input file, invokes ``python -m src.main`` inside the
cloned skip-trace-scraper repo, and reads the JSON output file.

Expected repo location:
    backend/tools/skiptrace/skip-trace-scraper/

The scraper is invoked with env vars:
    INPUT_FILE  — path to the JSON request
    OUTPUT_FILE — path where the scraper writes results

Input schema  (written to INPUT_FILE):
    {
        "name": "James E Whitsitt",
        "state": "Indiana",          // optional
        "city": "",                   // optional
        "extra": {}                   // any additional hints
    }

Output schema (read from OUTPUT_FILE):
    {
        "status": "ok" | "error",
        "results": { ... }           // scraper-specific payload
    }
"""

import json
import logging
import subprocess
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Resolve the scraper repo path relative to this file.
_SCRAPER_DIR = Path(__file__).parent / "skip-trace-scraper"


def run_skiptrace_scraper(
    name: str,
    state: str = "",
    city: str = "",
    extra: Optional[dict] = None,
    timeout_seconds: int = 60,
) -> str:
    """Run the skip-trace-scraper subprocess and return formatted results.

    Returns a human-readable string (successful results or error message).
    Designed to degrade gracefully — never raises, always returns a string.
    """
    if not _SCRAPER_DIR.is_dir():
        return (
            "[SkipTrace Scraper] Not installed. "
            "Clone the repo into backend/tools/skiptrace/skip-trace-scraper/"
        )

    input_file = Path("/tmp/skiptrace_input.json")
    output_file = Path("/tmp/skiptrace_output.json")

    input_data = {
        "name": name,
        "state": state,
        "city": city,
        "extra": extra or {},
    }

    try:
        input_file.write_text(json.dumps(input_data))

        # Remove stale output
        if output_file.exists():
            output_file.unlink()

        env = {
            **os.environ,
            "INPUT_FILE": str(input_file),
            "OUTPUT_FILE": str(output_file),
        }

        result = subprocess.run(
            ["python", "-m", "src.main"],
            cwd=str(_SCRAPER_DIR),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        if result.returncode != 0:
            stderr_snippet = (result.stderr or "")[:500]
            logger.warning("SkipTrace scraper failed (rc=%d): %s", result.returncode, stderr_snippet)
            return f"[SkipTrace Scraper] Process exited with code {result.returncode}:\n{stderr_snippet}"

        if not output_file.exists():
            return "[SkipTrace Scraper] Process completed but no output file was produced."

        raw = json.loads(output_file.read_text())
        status = raw.get("status", "unknown")

        if status == "error":
            return f"[SkipTrace Scraper] Error: {raw.get('message', raw)}"

        # Format results for LLM consumption
        results = raw.get("results", raw)
        return f"[SkipTrace Scraper] Live results for '{name}':\n{json.dumps(results, indent=2, default=str)}"

    except subprocess.TimeoutExpired:
        return f"[SkipTrace Scraper] Timed out after {timeout_seconds}s."
    except json.JSONDecodeError as e:
        return f"[SkipTrace Scraper] Invalid JSON output: {e}"
    except Exception as e:
        logger.exception("SkipTrace scraper unexpected error")
        return f"[SkipTrace Scraper] Error: {str(e)}"
    finally:
        # Cleanup temp files
        for f in (input_file, output_file):
            try:
                f.unlink(missing_ok=True)
            except OSError:
                pass
