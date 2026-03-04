"""NL → SSH command translation via LLM.

Takes a natural-language instruction (e.g. "check disk space on mainframe")
and uses the configured LLM provider to produce a structured command plan:

    {
        "host": "mainframe",
        "command": "df -h",
        "explanation": "Shows disk space usage on mainframe",
        "risk": "low"
    }
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional

from backend.console.hosts import hosts_summary, get_host, get_hosts
from backend.providers.factory import get_provider

# The LLM is prompted to return ONLY a JSON object — no markdown, no prose.
_SYSTEM_PROMPT = """\
You are Console Intelligence, a secure SSH command translator for the \
FinanceCommander AI Portal.

Your job: convert natural-language requests into a single JSON object that \
describes the SSH command to run.

{hosts}

RULES:
1. Respond with ONLY a valid JSON object — no markdown fences, no explanation.
2. The JSON MUST have these keys:
   - "host"  (string) — alias of the target host from the list above
   - "command" (string) — the exact shell command to run
   - "explanation" (string) — one-line description of what it does
   - "risk" (string) — "low", "medium", or "high"
3. If the user's request is ambiguous about which host, pick the most likely \
   or ask by returning {{"host": null, "command": null, "explanation": null, \
   "error": "Which host? Available: ..."}}
4. NEVER produce destructive commands (rm -rf /, mkfs, dd to disk, etc.).
5. If the request cannot be safely translated, return an error JSON: \
   {{"host": null, "command": null, "explanation": null, \
   "error": "reason"}}
6. Prefer concise, idiomatic Linux commands.
7. For multi-step tasks, chain with && or use a subshell.
8. Always use non-interactive flags where applicable (-y, --no-pager, etc).
"""


@dataclass
class CommandPlan:
    """Parsed LLM output."""
    host: Optional[str]
    command: Optional[str]
    explanation: Optional[str]
    risk: str = "low"
    error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return bool(self.host and self.command and not self.error)


def _extract_json(text: str) -> dict:
    """Extract a JSON object from LLM output, tolerating markdown fences."""
    # Strip markdown code fences if present
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def translate_command(
    user_input: str,
    provider_name: str = "anthropic",
    model: str = "claude-sonnet-4-20250514",
) -> CommandPlan:
    """Translate a natural-language request into a CommandPlan.

    Uses the configured provider/model to generate the SSH command.
    """
    provider = get_provider(provider_name)

    system = _SYSTEM_PROMPT.format(hosts=hosts_summary())

    response = await provider.send_message(
        messages=[{"role": "user", "content": user_input}],
        model=model,
        system_prompt=system,
        temperature=0.1,  # Low temp for deterministic command generation
        max_tokens=512,
    )

    try:
        data = _extract_json(response.content)
    except (json.JSONDecodeError, ValueError):
        return CommandPlan(
            host=None,
            command=None,
            explanation=None,
            error=f"LLM returned invalid JSON: {response.content[:200]}",
        )

    return CommandPlan(
        host=data.get("host"),
        command=data.get("command"),
        explanation=data.get("explanation"),
        risk=data.get("risk", "low"),
        error=data.get("error"),
    )
