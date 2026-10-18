"""Abstract transport interface for talking to a system under test (SUT).

Every transport (SSH, serial, local) implements the same small contract,
so the test runner and test cases don't need to know or care how the
bytes actually get to the target.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CommandResult:
    """Result of running a single command on the SUT."""
    command: str
    stdout: str
    stderr: str
    exit_code: int

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


class Transport(ABC):
    """Common interface every SUT transport must implement."""

    @abstractmethod
    def connect(self) -> None:
        """Establish the connection to the SUT. Must be called before run()."""

    @abstractmethod
    def run(self, command: str, timeout: float = 10.0) -> CommandResult:
        """Execute a single command on the SUT and return its result."""

    @abstractmethod
    def close(self) -> None:
        """Tear down the connection. Safe to call multiple times."""

    def __enter__(self) -> "Transport":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
