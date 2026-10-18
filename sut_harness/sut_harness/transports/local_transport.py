"""Local transport: runs commands as subprocesses on the host itself.

Used as a stand-in SUT for development and for the pytest suite, so the
harness can be exercised in CI without any real hardware attached.
"""
from __future__ import annotations

import subprocess

from .base import CommandResult, Transport


class LocalTransport(Transport):
    """Executes commands via the local shell. No real connection needed.

    Runs through the platform shell (shell=True) rather than exec'ing the
    first token directly, so shell builtins like `echo` work the same way
    on Windows (cmd.exe) as on Linux/macOS (sh) — the same command string
    that would work in an SSH session works here too.
    """

    def connect(self) -> None:
        pass  # nothing to set up — the "connection" is always available

    def run(self, command: str, timeout: float = 10.0) -> CommandResult:
        proc = subprocess.run(
            command,
            shell=True,
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
