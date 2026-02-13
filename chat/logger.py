"""Usage logging to CSV files."""

import csv
import hashlib
import os
from datetime import datetime, timezone

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
