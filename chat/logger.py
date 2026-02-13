"""Usage logging to CSV files."""

import csv
import os
from datetime import datetime, timezone

from config.pricing import estimate_cost
from config.settings import LOG_DIR


class UsageLogger:
    """Append per-request usage rows to a daily CSV log."""

    FIELDNAMES = [
        "timestamp",
        "user_email",
        "specialist_id",
        "model",
        "input_tokens",
        "output_tokens",
        "estimated_cost",
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
        model: str,
        input_tokens: int,
        output_tokens: int,
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
                    "user_email": user_email,
                    "specialist_id": specialist_id,
                    "model": model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "estimated_cost": f"{estimate_cost(model, input_tokens, output_tokens):.6f}",
                }
            )
