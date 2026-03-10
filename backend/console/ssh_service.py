"""Async SSH execution service for Console Intelligence.

Uses the system ssh binary via asyncio.subprocess for reliable SSH
command execution without library-level key scanning issues.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Optional

from backend.console.hosts import HostEntry


@dataclass
class SSHOutput:
    """A single chunk of SSH output."""
    stream: str  # "stdout" | "stderr" | "status"
    text: str


# ── Blocked commands ───────────────────────────────────────────

_BLOCKED_PATTERNS = [
    "rm -rf /",
    "mkfs",
    "dd if=",
    "> /dev/sd",
    "shutdown",
    "reboot",
    "halt",
    "init 0",
    "init 6",
    ":(){ :|:& };:",
    "chmod -R 777 /",
    "chown -R",
    "passwd",
    "userdel",
    "useradd",
    "visudo",
]


def _is_blocked(command: str) -> Optional[str]:
    """Return a reason string if the command is blocked, else None."""
    lower = command.lower().strip()
    for pattern in _BLOCKED_PATTERNS:
        if pattern.lower() in lower:
            return f"Blocked: command matches dangerous pattern '{pattern}'"
    return None


# ── SSH Execution ──────────────────────────────────────────────


async def execute_ssh_command(
    host: HostEntry,
    command: str,
    timeout: int = 30,
) -> AsyncGenerator[SSHOutput, None]:
    """Execute a command on a remote host via system ssh binary."""
    blocked = _is_blocked(command)
    if blocked:
        yield SSHOutput(stream="stderr", text=f"⛔ {blocked}\n")
        yield SSHOutput(stream="status", text="blocked")
        return

    ssh_args = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        "-o", "BatchMode=yes",
        "-o", "IdentitiesOnly=yes",
        "-p", str(host.port),
    ]
    if host.key_file:
        ssh_args += ["-i", host.key_file]

    ssh_args.append(f"{host.username}@{host.hostname}")
    ssh_args.append(command)

    try:
        proc = await asyncio.create_subprocess_exec(
            *ssh_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout_lines: list[SSHOutput] = []
        stderr_lines: list[SSHOutput] = []

        async def collect_stdout():
            while True:
                line = await asyncio.wait_for(proc.stdout.readline(), timeout=timeout)
                if not line:
                    break
                stdout_lines.append(
                    SSHOutput(stream="stdout", text=line.decode("utf-8", errors="replace"))
                )

        async def collect_stderr():
            while True:
                line = await asyncio.wait_for(proc.stderr.readline(), timeout=timeout)
                if not line:
                    break
                stderr_lines.append(
                    SSHOutput(stream="stderr", text=line.decode("utf-8", errors="replace"))
                )

        try:
            await asyncio.wait_for(
                asyncio.gather(collect_stdout(), collect_stderr()),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            yield SSHOutput(stream="stderr", text=f"⏱ Command timed out after {timeout}s\n")
            yield SSHOutput(stream="status", text="timeout")
            return

        for chunk in stdout_lines:
            yield chunk
        for chunk in stderr_lines:
            yield chunk

        exit_code = await proc.wait()
        yield SSHOutput(stream="status", text=str(exit_code))

    except Exception as exc:
        yield SSHOutput(stream="stderr", text=f"SSH error: {exc}\n")
        yield SSHOutput(stream="status", text="error")


async def test_connection(host: HostEntry) -> dict:
    """Test SSH connectivity to a host. Returns status dict."""
    result = {"alias": host.alias, "hostname": host.hostname, "status": "unknown"}
    try:
        chunks = []
        async for chunk in execute_ssh_command(host, "echo ok && hostname", timeout=10):
            chunks.append(chunk)

        status_chunk = next((c for c in chunks if c.stream == "status"), None)
        stdout = "".join(c.text for c in chunks if c.stream == "stdout").strip()

        if status_chunk and status_chunk.text == "0":
            result["status"] = "connected"
            result["hostname_resolved"] = stdout.split("\n")[-1] if stdout else ""
        else:
            result["status"] = "failed"
            result["error"] = "".join(c.text for c in chunks if c.stream == "stderr").strip()
    except Exception as exc:
        result["status"] = "error"
        result["error"] = str(exc)

    return result
