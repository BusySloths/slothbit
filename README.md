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

## Model catalog

“1-bit” is sometimes used loosely. Binary models generally use two weight
values such as `{-1, +1}`. BitNet b1.58 and other ternary models use
`{-1, 0, +1}`—three states carrying about 1.58 bits of information per
weight. A conventional model quantized to a 2-bit file after training is not
necessarily a native ternary model.

| Model family | Sizes | Weight type | Runtime | N150 suitability |
| --- | ---: | --- | --- | --- |
| [PrismML Bonsai](https://huggingface.co/prism-ml/models) | 1.7B, 4B, 8B, 27B | Binary / 1-bit | `llama.cpp` | 1.7B–8B recommended |
| [PrismML Ternary Bonsai](https://huggingface.co/collections/prism-ml/ternary-bonsai) | 1.7B, 4B, 8B, 27B | Ternary / 1.58-bit | `llama.cpp` | 1.7B–8B recommended |
| [Microsoft BitNet b1.58 2B-4T](https://huggingface.co/microsoft/bitnet-b1.58-2B-4T) | 2.4B | Native ternary | `bitnet.cpp` | Recommended baseline |
| [Falcon3 1.58-bit](https://huggingface.co/collections/tiiuae/falcon3) | 1B, 3B, 7B, 10B | Ternary | `bitnet.cpp` | 1B–3B recommended |
| [1bitLLM BitNet](https://huggingface.co/1bitLLM) | 0.7B, 3.3B | Ternary research models | `bitnet.cpp` | Good kernel baselines |
| [Llama3-8B-1.58-100B-tokens](https://huggingface.co/HF1BitLLM/Llama3-8B-1.58-100B-tokens) | 8B | Experimental ternary | `bitnet.cpp` | Usable, but slow |
| [TriLM 3.9B](https://huggingface.co/Green-Sky/TriLM_3.9B-GGUF) | 3.9B | Native ternary research model | GGUF / community tooling | Experimental |

The current SlothBit adapter supports the PrismML GGUF families. Microsoft
BitNet, Falcon, and older research checkpoints require the planned
`bitnet.cpp` backend. The 27B models are included for completeness but are not
practical on the current four-core Intel N150 test machine.

Switch between compatible Bonsai models without modifying source code:

```console
SLOTHBIT_MODEL=prism-ml/Bonsai-1.7B-gguf:Q1_0 \
  uv run slothbit infer "Explain binary weights."

SLOTHBIT_MODEL=prism-ml/Bonsai-4B-gguf:Q1_0 \
  uv run slothbit infer "Explain binary weights."
```

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
