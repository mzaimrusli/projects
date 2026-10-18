"""Local transport: runs commands as subprocesses on the host itself.

Used as a stand-in SUT for development and for the pytest suite, so the
harness can be exercised in CI without any real hardware attached.
"""
from __future__ import annotations

import shlex
import subprocess

from .base import CommandResult, Transport


class LocalTransport(Transport):
    """Executes commands via the local shell. No real connection needed."""

    def connect(self) -> None:
        pass  # nothing to set up — the "connection" is always available

    def run(self, command: str, timeout: float = 10.0) -> CommandResult:
        proc = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return CommandResult(
            command=command,
            stdout=proc.stdout,
            stderr=proc.stderr,
            exit_code=proc.returncode,
        )

    def close(self) -> None:
        pass
