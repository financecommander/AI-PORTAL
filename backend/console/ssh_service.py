"""Async SSH execution service for Console Intelligence.

Uses asyncssh for non-blocking SSH command execution with live output
streaming.  Falls back to asyncio.subprocess if asyncssh is not installed
(uses the system ssh binary).
"""

from __future__ import annotations

import asyncio
import os
import shlex
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Optional

from backend.console.hosts import HostEntry

# Try asyncssh, fall back to subprocess-based SSH
try:
    import asyncssh
    _HAS_ASYNCSSH = True
except ImportError:
    _HAS_ASYNCSSH = False


@dataclass
class SSHOutput:
    """A single chunk of SSH output."""
    stream: str  # "stdout" | "stderr" | "status"
    text: str


# ── Blocked commands ───────────────────────────────────────────
# Commands that should never be executed remotely through the portal.

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
    ":(){ :|:& };:",  # fork bomb
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
    """Execute a command on a remote host and yield output chunks.

    Streams stdout/stderr line-by-line as they arrive, then yields
    a final "status" chunk with the exit code.
    """
    # Safety check
    blocked = _is_blocked(command)
    if blocked:
        yield SSHOutput(stream="stderr", text=f"⛔ {blocked}\n")
        yield SSHOutput(stream="status", text="blocked")
        return

    if _HAS_ASYNCSSH:
        async for chunk in _exec_asyncssh(host, command, timeout):
            yield chunk
    else:
        async for chunk in _exec_subprocess(host, command, timeout):
            yield chunk


async def _exec_asyncssh(
    host: HostEntry,
    command: str,
    timeout: int,
) -> AsyncGenerator[SSHOutput, None]:
    """Execute via asyncssh library."""
    connect_kwargs: dict = dict(
        host=host.hostname,
        port=host.port,
        username=host.username,
        known_hosts=None,  # Accept all host keys (configurable in prod)
        agent_path=None,   # Don't use SSH agent
        config=(),         # Don't read SSH config files
    )
    if host.key_file:
        connect_kwargs["client_keys"] = [host.key_file]
    else:
        connect_kwargs["client_keys"] = []

    try:
        async with asyncssh.connect(**connect_kwargs) as conn:
            result = await asyncio.wait_for(
                conn.run(command, check=False),
                timeout=timeout,
            )
            if result.stdout:
                for line in result.stdout.splitlines(keepends=True):
                    yield SSHOutput(stream="stdout", text=line)
            if result.stderr:
                for line in result.stderr.splitlines(keepends=True):
                    yield SSHOutput(stream="stderr", text=line)
            yield SSHOutput(
                stream="status",
                text=str(result.exit_status if result.exit_status is not None else -1),
            )
    except asyncio.TimeoutError:
        yield SSHOutput(stream="stderr", text=f"⏱ Command timed out after {timeout}s\n")
        yield SSHOutput(stream="status", text="timeout")
    except Exception as exc:
        yield SSHOutput(stream="stderr", text=f"SSH error: {exc}\n")
        yield SSHOutput(stream="status", text="error")


async def _exec_subprocess(
    host: HostEntry,
    command: str,
    timeout: int,
) -> AsyncGenerator[SSHOutput, None]:
    """Execute via system ssh binary (fallback)."""
    ssh_args = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        "-o", "BatchMode=yes",
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

        async def _read_stream(stream, name):
            while True:
                line = await asyncio.wait_for(stream.readline(), timeout=timeout)
                if not line:
                    break
                yield SSHOutput(stream=name, text=line.decode("utf-8", errors="replace"))

        # Read stdout and stderr concurrently
        stdout_lines: list[SSHOutput] = []
        stderr_lines: list[SSHOutput] = []

        async def collect_stdout():
            async for chunk in _read_stream(proc.stdout, "stdout"):
                stdout_lines.append(chunk)

        async def collect_stderr():
            async for chunk in _read_stream(proc.stderr, "stderr"):
                stderr_lines.append(chunk)

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
