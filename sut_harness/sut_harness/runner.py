"""Minimal test runner: executes a command on a SUT and checks its output.

This is the smallest possible version of the pattern used in larger
validation frameworks: a host process drives a target over some
transport, runs a known command, and asserts on the result rather than
trusting the target's exit code alone (targets lie, or don't have one).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from .transports.base import CommandResult, Transport

log = logging.getLogger("sut_harness")


@dataclass
class TestOutcome:
    name: str
    passed: bool
    detail: str


class HelloWorldTest:
    """Smoke test: run a command on the SUT and expect a specific string back.

    Defaults to printing "Hello, World!" but any command/expected pair
    works — this is deliberately the simplest possible health check,
    the kind you run first on a new target before trusting anything else.
    """

    name = "hello_world"

    def __init__(
        self,
        command: str = 'echo "Hello, World!"',
        expected: str = "Hello, World!",
    ) -> None:
        self.command = command
        self.expected = expected

    def run(self, transport: Transport) -> TestOutcome:
        result: CommandResult = transport.run(self.command)

        if self.expected not in result.stdout:
            return TestOutcome(
                name=self.name,
                passed=False,
                detail=(
                    f"expected {self.expected!r} in stdout, got "
                    f"stdout={result.stdout!r} stderr={result.stderr!r} "
                    f"exit_code={result.exit_code}"
                ),
            )

        return TestOutcome(
            name=self.name,
            passed=True,
            detail=f"found {self.expected!r} in SUT response",
        )


def run_tests(transport: Transport, tests: list[HelloWorldTest]) -> list[TestOutcome]:
    """Run each test against an already-connected transport, logging as it goes."""
    outcomes = []
    for test in tests:
        outcome = test.run(transport)
        level = logging.INFO if outcome.passed else logging.ERROR
        log.log(level, "%s: %s - %s", test.name, "PASS" if outcome.passed else "FAIL", outcome.detail)
        outcomes.append(outcome)
    return outcomes
