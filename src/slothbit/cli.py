"""Command-line entry point."""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import sys

from .config import DEFAULT_MODEL, Settings
from .llama import (
    LlamaNotFoundError,
    build_cli_command,
    build_server_command,
    find_executable,
    run,
)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    commands.add_parser("doctor", help="check local inference prerequisites")

    infer = commands.add_parser("infer", help="run one local prompt")
    infer.add_argument("prompt")
    infer.add_argument("--predict", type=int, default=256)

    commands.add_parser("serve", help="start the local OpenAI-compatible server")
    return root


def doctor() -> int:
    checks = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "uv": shutil.which("uv") or "missing",
        "llama-cli": find_executable("cli") or "missing",
        "llama-server": find_executable("server") or "missing",
        "model": os.getenv("SLOTHBIT_MODEL", DEFAULT_MODEL),
    }
    for name, value in checks.items():
        print(f"{name:13} {value}")
    if find_executable("cli") is None:
        print("\nInstall llama.cpp, or place it in .tools/llama.cpp.")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "doctor":
        return doctor()

    settings = Settings.from_env()
    try:
        if args.command == "infer":
            return run(build_cli_command(settings, args.prompt, args.predict))
        if args.command == "serve":
            return run(build_server_command(settings))
    except LlamaNotFoundError as error:
        print(f"error: {error}. Run `uv run slothbit doctor`.", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
