"""Serial (UART) transport: talks to a SUT over a serial console.

Common for bare-metal / bring-up scenarios where the target has no
network stack yet and the only way in is a debug UART. Unlike SSH,
a raw serial console has no concept of a command "exit code" — success
is judged by whether the expected text showed up in the response, which
is exactly how it works in practice when bringing up new hardware.
"""
from __future__ import annotations

import time

from .base import CommandResult, Transport

try:
    import serial
except ImportError:  # pragma: no cover - optional dependency
    serial = None


class SerialTransport(Transport):
    def __init__(self, port: str, baudrate: int = 115200) -> None:
        if serial is None:
            raise RuntimeError(
                "pyserial is required for SerialTransport: pip install pyserial"
            )
        self.port = port
        self.baudrate = baudrate
        self._conn: "serial.Serial | None" = None

    def connect(self) -> None:
        self._conn = serial.Serial(self.port, self.baudrate, timeout=1)

    def run(self, command: str, timeout: float = 10.0) -> CommandResult:
        if self._conn is None:
            raise RuntimeError("SerialTransport.connect() must be called first")

        self._conn.reset_input_buffer()
        self._conn.write((command + "\r\n").encode())

        deadline = time.monotonic() + timeout
        lines: list[str] = []
        while time.monotonic() < deadline:
            line = self._conn.readline().decode(errors="replace")
            if line:
                lines.append(line)
            else:
                break  # no more data arriving before the read timeout

        output = "".join(lines)
        # A raw UART console has no exit-code concept — treat "got a
        # response" as success; callers judge pass/fail from the output.
        return CommandResult(
            command=command,
            stdout=output,
            stderr="",
            exit_code=0 if output else 1,
        )

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
