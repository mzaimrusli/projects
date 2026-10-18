"""SSH transport: runs commands on a remote SUT over an SSH connection.

Typical use case: a target machine (server, dev board running Linux,
BMC) reachable over the network, where the harness logs in and runs a
command non-interactively, same as a CI runner would.
"""
from __future__ import annotations

from .base import CommandResult, Transport

try:
    import paramiko
except ImportError:  # pragma: no cover - optional dependency
    paramiko = None


class SSHTransport(Transport):
    def __init__(
        self,
        host: str,
        username: str,
        password: str | None = None,
        key_filename: str | None = None,
        port: int = 22,
    ) -> None:
        if paramiko is None:
            raise RuntimeError(
                "paramiko is required for SSHTransport: pip install paramiko"
            )
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self._client: "paramiko.SSHClient | None" = None

    def connect(self) -> None:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            key_filename=self.key_filename,
        )
        self._client = client

    def run(self, command: str, timeout: float = 10.0) -> CommandResult:
        if self._client is None:
            raise RuntimeError("SSHTransport.connect() must be called first")

        _, stdout, stderr = self._client.exec_command(command, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        return CommandResult(
            command=command,
            stdout=stdout.read().decode(errors="replace"),
            stderr=stderr.read().decode(errors="replace"),
            exit_code=exit_code,
        )

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
