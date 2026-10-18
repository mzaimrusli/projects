"""Command-line entry point: pick a transport, connect, run the smoke test.

Examples:
    python -m sut_harness.cli --transport local
    python -m sut_harness.cli --transport ssh --host 10.0.0.5 --user root
    python -m sut_harness.cli --transport serial --port /dev/ttyUSB0
"""
from __future__ import annotations

import argparse
import logging
import sys

from .runner import HelloWorldTest, run_tests
from .transports import LocalTransport, SSHTransport, SerialTransport
from .transports.base import Transport


def build_transport(args: argparse.Namespace) -> Transport:
    if args.transport == "local":
        return LocalTransport()

    if args.transport == "ssh":
        if not args.host or not args.user:
            raise SystemExit("--host and --user are required for --transport ssh")
        return SSHTransport(
            host=args.host,
            username=args.user,
            password=args.password,
            key_filename=args.key,
        )

    if args.transport == "serial":
        if not args.port:
            raise SystemExit("--port is required for --transport serial")
        return SerialTransport(port=args.port, baudrate=args.baud)

    raise SystemExit(f"unknown transport: {args.transport}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a smoke test against a SUT")
    parser.add_argument("--transport", choices=["local", "ssh", "serial"], default="local")
    parser.add_argument("--host", help="SSH: hostname/IP of the SUT")
    parser.add_argument("--user", help="SSH: username")
    parser.add_argument("--password", help="SSH: password (prefer --key)")
    parser.add_argument("--key", help="SSH: path to private key file")
    parser.add_argument("--port", help="Serial: device path, e.g. /dev/ttyUSB0 or COM3")
    parser.add_argument("--baud", type=int, default=115200, help="Serial: baud rate")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    transport = build_transport(args)
    with transport:
        outcomes = run_tests(transport, [HelloWorldTest()])

    failed = [o for o in outcomes if not o.passed]
    if failed:
        print(f"\n{len(failed)}/{len(outcomes)} test(s) failed")
        return 1

    print(f"\n{len(outcomes)}/{len(outcomes)} test(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
