# SlothBit

**Low-bit models, high-curiosity experiments.**

SlothBit is a reproducible local testbed for 1-bit and ternary neural
networks, BitNet research, and low-bit LLM inference. Its first supported
target is PrismML's 1-bit Bonsai 8B model, run through `llama.cpp` on Linux
or macOS.

> [!NOTE]
> Bonsai 8B is a PrismML model inspired by low-bit work such as Microsoft's
> BitNet. It is distributed as a `llama.cpp`-compatible GGUF; it is not one of
> the models listed as supported by Microsoft's `bitnet.cpp`.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- A recent [llama.cpp](https://github.com/ggml-org/llama.cpp) build providing
  `llama-cli` and `llama-server`
- Roughly 2 GB of free disk space for the model/cache and enough RAM for its
  1.16 GB GGUF plus runtime state

## Quick start

Install `llama.cpp` using its platform instructions, then:

```console
uv sync
uv run slothbit doctor
uv run slothbit infer "Why are ternary weights interesting?"
```

The first inference downloads `prism-ml/Bonsai-8B-gguf:Q1_0` from Hugging
Face into the normal llama.cpp cache. No model weights are committed here.

The CLI searches `PATH` first, then `.tools/llama.cpp`. Override the latter
with `SLOTHBIT_LLAMA_CPP_DIR` when using a custom local build.

To expose an OpenAI-compatible local endpoint:

```console
uv run slothbit serve
curl http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Hello!"}]}'
```

## Configuration

Copy `.env.example` as a reference and export the variables in your shell.
The CLI intentionally does not load `.env` implicitly.

| Variable | Default | Purpose |
| --- | --- | --- |
| `SLOTHBIT_MODEL` | `prism-ml/Bonsai-8B-gguf:Q1_0` | HF shorthand or local `.gguf` path |
| `SLOTHBIT_CONTEXT_SIZE` | `4096` | Context window used by llama.cpp |
| `SLOTHBIT_THREADS` | auto | CPU worker threads |
| `SLOTHBIT_GPU_LAYERS` | `0` | Layers offloaded to a supported GPU |
| `SLOTHBIT_HOST` | `127.0.0.1` | Server bind address |
| `SLOTHBIT_PORT` | `8080` | Server port |
| `SLOTHBIT_LLAMA_CPP_DIR` | `.tools/llama.cpp` | Local runtime directory |

For CPU-only inference, keep GPU layers at `0`. For a compatible GPU build,
increase it experimentally; `99` is a convenient request to offload all
possible layers.

## Development

```console
uv sync --all-groups
make check
```

The Python adapter is deliberately thin. Future backends can implement the
same infer/serve boundary for Microsoft's `bitnet.cpp`, MLX, or training
frameworks without coupling experiment code to a single runtime.

## Roadmap

- Record repeatable latency, throughput, memory, and quality benchmarks
- Add an official `bitnet.cpp` backend and Microsoft's b1.58 2B-4T baseline
- Add binary/ternary fine-tuning and conversion experiments
- Persist experiment manifests and machine-readable results under `results/`

## License

Project code is MIT licensed. Model weights and third-party runtimes retain
their respective licenses; Bonsai 8B is published under Apache-2.0.
