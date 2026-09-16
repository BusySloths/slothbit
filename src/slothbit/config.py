"""Runtime configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_MODEL = "prism-ml/Bonsai-8B-gguf:Q1_0"


@dataclass(frozen=True, slots=True)
class Settings:
    """Settings shared by local llama.cpp commands."""

    model: str = DEFAULT_MODEL
    host: str = "127.0.0.1"
    port: int = 8080
    context_size: int = 4096
    threads: int | None = None
    gpu_layers: int = 0

    @classmethod
    def from_env(cls) -> Settings:
        threads = os.getenv("SLOTHBIT_THREADS")
        return cls(
            model=os.getenv("SLOTHBIT_MODEL", DEFAULT_MODEL),
            host=os.getenv("SLOTHBIT_HOST", "127.0.0.1"),
            port=int(os.getenv("SLOTHBIT_PORT", "8080")),
            context_size=int(os.getenv("SLOTHBIT_CONTEXT_SIZE", "4096")),
            threads=int(threads) if threads else None,
            gpu_layers=int(os.getenv("SLOTHBIT_GPU_LAYERS", "0")),
        )
