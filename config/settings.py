"""App-wide constants and defaults."""

import os

APP_TITLE = "FinanceCommander AI Portal"

# Default model settings
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE: float = 0.7
DEFAULT_MAX_TOKENS: int = 2048

# Paths
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
SPECIALISTS_FILE = os.path.join(
    os.path.dirname(__file__), "specialists.json"
)

# Auth
ALLOWED_DOMAINS: list[str] = ["financecommander.com"]

# Session
SESSION_TIMEOUT_SECONDS: int = 1800  # 30 minutes

# Rate limiting
RATE_LIMIT_REQUESTS: int = 60           # Requests per window
RATE_LIMIT_WINDOW_SECONDS: int = 3600   # 1 hour window

# Chat
MAX_CHAT_HISTORY: int = 50              # Messages per specialist
STREAMING_ENABLED: bool = True           # Global streaming toggle
STREAM_CHUNK_TIMEOUT: float = 30.0       # Seconds before stream timeout

# Specialist validation
MAX_SPECIALIST_NAME_LENGTH: int = 100
MAX_SYSTEM_PROMPT_LENGTH: int = 4000
MAX_DESCRIPTION_LENGTH: int = 500
MIN_MAX_TOKENS: int = 256
MAX_MAX_TOKENS: int = 8192

# Logging
LOG_DATE_FORMAT: str = "%Y-%m-%d"
