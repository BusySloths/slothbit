"""Small, inspectable adapter around llama.cpp executables."""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

from .config import Settings


class LlamaNotFoundError(RuntimeError):
    """Raised when a llama.cpp executable is unavailable."""


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def find_executable(kind: str) -> str | None:
    """Find llama.cpp on PATH or in this project's local tools directory."""
    names = {
        "cli": ("llama-cli", "main"),
        "server": ("llama-server", "server"),
    }
    if kind not in names:
        raise ValueError(f"Unknown llama.cpp executable kind: {kind}")
    if executable := next((path for name in names[kind] if (path := shutil.which(name))), None):
        return executable

    local_dir = Path(os.getenv("SLOTHBIT_LLAMA_CPP_DIR", PROJECT_ROOT / ".tools/llama.cpp"))
    return next(
        (str(path) for name in names[kind] if (path := local_dir / name).is_file()),
        None,
    )


def model_args(model: str) -> list[str]:
    """Translate a local GGUF path or a Hugging Face shorthand into CLI arguments."""
    return ["-m", model] if model.endswith(".gguf") else ["-hf", model]


def build_cli_command(settings: Settings, prompt: str, predict: int = 256) -> list[str]:
    executable = find_executable("cli")
    if executable is None:
        raise LlamaNotFoundError("llama-cli was not found on PATH")
    command = [
        executable,
        *model_args(settings.model),
        "--ctx-size",
        str(settings.context_size),
        "--n-predict",
        str(predict),
        "--prompt",
        prompt,
    ]
    if settings.threads is not None:
        command.extend(("--threads", str(settings.threads)))
    if settings.gpu_layers:
        command.extend(("--n-gpu-layers", str(settings.gpu_layers)))
    return command


def build_server_command(settings: Settings) -> list[str]:
    executable = find_executable("server")
    if executable is None:
        raise LlamaNotFoundError("llama-server was not found on PATH")
    command = [
        executable,
        *model_args(settings.model),
        "--host",
        settings.host,
        "--port",
        str(settings.port),
        "--ctx-size",
        str(settings.context_size),
    ]
    if settings.threads is not None:
        command.extend(("--threads", str(settings.threads)))
    if settings.gpu_layers:
        command.extend(("--n-gpu-layers", str(settings.gpu_layers)))
    return command


def run(command: Sequence[str]) -> int:
    """Run llama.cpp interactively and propagate its exit code."""
    return subprocess.run(command, check=False).returncode
