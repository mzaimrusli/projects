# sut-harness

A minimal host-to-SUT (system under test) test automation harness: a
host process connects to a target over some transport, runs a command,
and checks the response — the same basic pattern used in larger
validation frameworks for bringing up and sanity-checking new hardware.

This is a small, from-scratch, general-purpose version of that pattern
(not tied to any specific employer's codebase or tooling).

## Why this shape

- **Pluggable transport layer.** The host doesn't care *how* it talks to
  the target — `LocalTransport` (subprocess, for development/CI),
  `SSHTransport` (paramiko, for a networked Linux target), and
  `SerialTransport` (pyserial, for a UART console on bare-metal/bring-up
  targets with no network stack yet) all implement the same three-method
  interface (`connect` / `run` / `close`).
- **Judge success from output, not just exit code.** A raw serial
  console has no concept of an exit code at all, and even on networked
  targets, "the process returned 0" isn't always trustworthy on its own.
  The harness checks for an expected string in the response, which is
  how you'd actually validate a target that might be mid-bring-up.
- **No hardware required to test the harness itself.** The pytest suite
  runs entirely against `LocalTransport`, so the logic is verified in
  any CI environment — real SSH/serial targets are only needed for an
  actual hardware run.

## Usage

```bash
pip install -r requirements.txt

# Run against the local machine (no real SUT needed)
python -m sut_harness.cli --transport local

# Run against a networked Linux target over SSH
python -m sut_harness.cli --transport ssh --host 10.0.0.5 --user root --key ~/.ssh/id_rsa

# Run against a bare-metal target over a debug UART
python -m sut_harness.cli --transport serial --port /dev/ttyUSB0 --baud 115200
```

## Tests

```bash
pytest
```

## Structure

```
sut_harness/
├── runner.py                   # HelloWorldTest + run_tests(): the actual test logic
├── cli.py                      # argparse entry point, picks a transport and runs
└── transports/
    ├── base.py                 # Transport ABC + CommandResult
    ├── local_transport.py      # subprocess-based (dev / CI)
    ├── ssh_transport.py        # paramiko-based
    └── serial_transport.py     # pyserial-based
tests/
└── test_runner.py              # exercises the harness via LocalTransport
```
