"""App-wide constants and defaults."""

import os

APP_TITLE = "Calculus AI Portal"
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
SPECIALISTS_FILE = os.path.join(
    os.path.dirname(__file__), "specialists.json"
)
ALLOWED_DOMAINS = ["calculus.com"]
