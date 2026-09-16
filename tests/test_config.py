from slothbit.config import DEFAULT_MODEL, Settings


def test_defaults(monkeypatch):
    for name in (
        "SLOTHBIT_MODEL",
        "SLOTHBIT_HOST",
        "SLOTHBIT_PORT",
        "SLOTHBIT_CONTEXT_SIZE",
        "SLOTHBIT_THREADS",
        "SLOTHBIT_GPU_LAYERS",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = Settings.from_env()

    assert settings.model == DEFAULT_MODEL
    assert settings.port == 8080
    assert settings.threads is None


def test_environment_overrides(monkeypatch):
    monkeypatch.setenv("SLOTHBIT_MODEL", "/models/test.gguf")
    monkeypatch.setenv("SLOTHBIT_THREADS", "6")
    monkeypatch.setenv("SLOTHBIT_GPU_LAYERS", "12")

    settings = Settings.from_env()

    assert settings.model == "/models/test.gguf"
    assert settings.threads == 6
    assert settings.gpu_layers == 12
