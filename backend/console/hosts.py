"""Host registry for Console Intelligence.

Hosts are loaded from the CONSOLE_HOSTS_FILE (default: console_hosts.yaml)
and cached in-memory.  Each host entry looks like:

  - alias: mainframe
    hostname: 10.0.0.5
    username: deploy
    port: 22
    description: Primary GPU workstation
    tags: [gpu, training]

SSH keys are expected in ~/.ssh/ or specified per-host via ``key_file``.
"""

from __future__ import annotations

import os
import json
import yaml
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class HostEntry:
    """A single SSH host."""
    alias: str
    hostname: str
    username: str = "root"
    port: int = 22
    description: str = ""
    tags: list[str] = field(default_factory=list)
    key_file: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


_HOST_REGISTRY: dict[str, HostEntry] = {}
_LOADED = False


def _load_hosts() -> None:
    """Load hosts from console_hosts.yaml (or env override)."""
    global _HOST_REGISTRY, _LOADED
    if _LOADED:
        return

    hosts_file = os.getenv(
        "CONSOLE_HOSTS_FILE",
        str(Path(__file__).resolve().parent.parent.parent / "console_hosts.yaml"),
    )

    if not Path(hosts_file).exists():
        # Fall back to env-based single-host config for quick setup
        env_host = os.getenv("CONSOLE_SSH_HOST")
        env_user = os.getenv("CONSOLE_SSH_USER", "root")
        if env_host:
            entry = HostEntry(
                alias=os.getenv("CONSOLE_SSH_ALIAS", "default"),
                hostname=env_host,
                username=env_user,
                port=int(os.getenv("CONSOLE_SSH_PORT", "22")),
                description=os.getenv("CONSOLE_SSH_DESC", "Default host"),
                key_file=str(Path(os.getenv("CONSOLE_SSH_KEY")).expanduser()) if os.getenv("CONSOLE_SSH_KEY") else None,
            )
            _HOST_REGISTRY[entry.alias] = entry
        _LOADED = True
        return

    with open(hosts_file, "r") as f:
        data = yaml.safe_load(f) or []

    for item in data:
        raw_key = item.get("key_file")
        entry = HostEntry(
            alias=item["alias"],
            hostname=item["hostname"],
            username=item.get("username", "root"),
            port=item.get("port", 22),
            description=item.get("description", ""),
            tags=item.get("tags", []),
            key_file=str(Path(raw_key).expanduser()) if raw_key else None,
        )
        _HOST_REGISTRY[entry.alias] = entry

    _LOADED = True


def get_hosts() -> list[HostEntry]:
    """Return all configured hosts."""
    _load_hosts()
    return list(_HOST_REGISTRY.values())


def get_host(alias: str) -> Optional[HostEntry]:
    """Return a single host by alias."""
    _load_hosts()
    return _HOST_REGISTRY.get(alias)


def reload_hosts() -> None:
    """Force reload hosts from config."""
    global _LOADED
    _LOADED = False
    _HOST_REGISTRY.clear()
    _load_hosts()


def hosts_summary() -> str:
    """Return a human-readable summary for the LLM system prompt."""
    _load_hosts()
    if not _HOST_REGISTRY:
        return "No hosts configured."
    lines = []
    for h in _HOST_REGISTRY.values():
        tags = f" [{', '.join(h.tags)}]" if h.tags else ""
        lines.append(f"  - {h.alias}: {h.description or h.hostname}{tags}")
    return "Available hosts:\n" + "\n".join(lines)
