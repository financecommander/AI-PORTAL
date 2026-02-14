"""Usage logging to CSV files."""

import csv
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

from config.pricing import estimate_cost
from config.settings import LOG_DIR


def _hash_email(email: str) -> str:
    """Return a SHA-256 hex digest of the lowercased email address."""
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()


class UsageLogger:
    """Append per-request usage rows to a daily CSV log."""

    FIELDNAMES = [
        "timestamp",
        "user_email_hash",
        "specialist_id",
        "specialist_name",
        "provider",
        "model",
        "input_tokens",
        "output_tokens",
        "estimated_cost_usd",
        "latency_ms",
        "success",
    ]

    def __init__(self, log_dir: str | None = None):
        self.log_dir = log_dir or LOG_DIR
        os.makedirs(self.log_dir, exist_ok=True)

    def _log_path(self) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"usage_{date_str}.csv")

    def log(
        self,
        user_email: str,
        specialist_id: str,
        specialist_name: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        success: bool,
    ) -> None:
        """Append a single usage row."""
        path = self._log_path()
        file_exists = os.path.exists(path)

        with open(path, "a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=self.FIELDNAMES)
            if not file_exists:
                writer.writeheader()
            writer.writerow(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "user_email_hash": _hash_email(user_email),
                    "specialist_id": specialist_id,
                    "specialist_name": specialist_name,
                    "provider": provider,
                    "model": model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "estimated_cost_usd": f"{estimate_cost(model, input_tokens, output_tokens):.6f}",
                    "latency_ms": latency_ms,
                    "success": success,
                }
            )

    def get_specialist_stats(self, specialist_id: str) -> dict:
        """Aggregate usage stats for a specialist from CSV logs.

        Scans all daily CSV files in the log directory and returns a
        summary dict with the following keys:

        - ``total_requests`` (int)
        - ``total_tokens`` (int)  – input + output
        - ``total_cost`` (float)
        - ``avg_latency_ms`` (float)
        - ``success_rate`` (float)  – 0.0 to 1.0
        - ``last_used`` (str | None)  – ISO timestamp of last request
        """
        stats: dict = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "avg_latency_ms": 0.0,
            "success_rate": 0.0,
            "last_used": None,
        }

        total_latency = 0.0
        successes = 0
        last_ts: str | None = None

        log_dir = Path(self.log_dir)
        if not log_dir.exists():
            return stats

        for csv_path in sorted(log_dir.glob("usage_*.csv")):
            try:
                with open(csv_path, newline="", encoding="utf-8") as fh:
                    reader = csv.DictReader(fh)
                    for row in reader:
                        if row.get("specialist_id") != specialist_id:
                            continue
                        stats["total_requests"] += 1
                        inp = int(row.get("input_tokens", 0))
                        out = int(row.get("output_tokens", 0))
                        stats["total_tokens"] += inp + out
                        stats["total_cost"] += float(row.get("estimated_cost_usd", 0))
                        total_latency += float(row.get("latency_ms", 0))
                        if row.get("success", "").lower() == "true":
                            successes += 1
                        ts = row.get("timestamp")
                        if ts and (last_ts is None or ts > last_ts):
                            last_ts = ts
            except (OSError, csv.Error):
                continue

        if stats["total_requests"] > 0:
            stats["avg_latency_ms"] = total_latency / stats["total_requests"]
            stats["success_rate"] = successes / stats["total_requests"]

        stats["last_used"] = last_ts
        return stats
