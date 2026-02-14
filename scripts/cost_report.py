#!/usr/bin/env python3
"""Cost report generator for FinanceCommander AI Portal.

Reads all daily CSV usage logs and produces a summary report grouped by
date, provider, model, and specialist. Outputs to stdout in Markdown or
CSV format.

Usage:
    python scripts/cost_report.py                 # Markdown (default)
    python scripts/cost_report.py --format csv     # CSV output
    python scripts/cost_report.py --days 7         # Last 7 days only
    python scripts/cost_report.py --log-dir /path  # Custom log directory
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to path so we can import config
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import LOG_DIR


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Portal cost report")
    parser.add_argument(
        "--format",
        choices=["markdown", "csv"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=0,
        help="Limit to last N days (0 = all time)",
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default=LOG_DIR,
        help="Path to usage‐log directory",
    )
    return parser.parse_args()


def _collect_rows(log_dir: str, days: int) -> list[dict]:
    """Read all CSV files and return filtered rows."""
    log_path = Path(log_dir)
    if not log_path.exists():
        return []

    cutoff: datetime | None = None
    if days > 0:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    rows: list[dict] = []
    for csv_file in sorted(log_path.glob("usage_*.csv")):
        try:
            with open(csv_file, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    if cutoff:
                        ts_str = row.get("timestamp", "")
                        try:
                            ts = datetime.fromisoformat(ts_str)
                            if ts < cutoff:
                                continue
                        except ValueError:
                            continue
                    rows.append(row)
        except (OSError, csv.Error):
            continue
    return rows


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def _aggregate(rows: list[dict]) -> dict:
    """Aggregate rows into summary dicts keyed by various dimensions."""
    by_date: dict[str, dict] = defaultdict(
        lambda: {"requests": 0, "tokens": 0, "cost": 0.0}
    )
    by_provider: dict[str, dict] = defaultdict(
        lambda: {"requests": 0, "tokens": 0, "cost": 0.0}
    )
    by_model: dict[str, dict] = defaultdict(
        lambda: {"requests": 0, "tokens": 0, "cost": 0.0}
    )
    by_specialist: dict[str, dict] = defaultdict(
        lambda: {"requests": 0, "tokens": 0, "cost": 0.0}
    )

    grand = {"requests": 0, "tokens": 0, "cost": 0.0}

    for row in rows:
        tokens = int(row.get("input_tokens", 0)) + int(row.get("output_tokens", 0))
        cost = float(row.get("estimated_cost_usd", 0))
        date = row.get("timestamp", "")[:10]
        provider = row.get("provider", "unknown")
        model = row.get("model", "unknown")
        specialist = row.get("specialist_name", "unknown")

        for d, key in [
            (by_date, date),
            (by_provider, provider),
            (by_model, model),
            (by_specialist, specialist),
        ]:
            d[key]["requests"] += 1
            d[key]["tokens"] += tokens
            d[key]["cost"] += cost

        grand["requests"] += 1
        grand["tokens"] += tokens
        grand["cost"] += cost

    return {
        "grand": grand,
        "by_date": dict(by_date),
        "by_provider": dict(by_provider),
        "by_model": dict(by_model),
        "by_specialist": dict(by_specialist),
    }


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def _md_table(title: str, data: dict[str, dict]) -> str:
    """Render a section as a Markdown table."""
    lines = [f"### {title}\n"]
    lines.append("| Key | Requests | Tokens | Cost (USD) |")
    lines.append("|-----|----------|--------|------------|")
    for key in sorted(data):
        d = data[key]
        lines.append(f"| {key} | {d['requests']:,} | {d['tokens']:,} | ${d['cost']:.4f} |")
    lines.append("")
    return "\n".join(lines)


def _render_markdown(agg: dict) -> str:
    grand = agg["grand"]
    parts = [
        "# AI Portal Cost Report\n",
        f"**Total requests:** {grand['requests']:,}  ",
        f"**Total tokens:** {grand['tokens']:,}  ",
        f"**Total cost:** ${grand['cost']:.4f}\n",
        _md_table("By Date", agg["by_date"]),
        _md_table("By Provider", agg["by_provider"]),
        _md_table("By Model", agg["by_model"]),
        _md_table("By Specialist", agg["by_specialist"]),
    ]
    return "\n".join(parts)


def _render_csv(agg: dict) -> str:
    import io

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["dimension", "key", "requests", "tokens", "cost_usd"])

    for dimension in ("by_date", "by_provider", "by_model", "by_specialist"):
        for key in sorted(agg[dimension]):
            d = agg[dimension][key]
            writer.writerow([dimension, key, d["requests"], d["tokens"], f"{d['cost']:.6f}"])

    return output.getvalue()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    args = _parse_args()
    rows = _collect_rows(args.log_dir, args.days)

    if not rows:
        print("No usage data found.", file=sys.stderr)
        sys.exit(0)

    agg = _aggregate(rows)

    if args.format == "csv":
        print(_render_csv(agg), end="")
    else:
        print(_render_markdown(agg))


if __name__ == "__main__":
    main()
