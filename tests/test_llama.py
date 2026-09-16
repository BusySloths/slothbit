from slothbit.config import Settings
from slothbit.llama import build_cli_command, build_server_command, find_executable, model_args


def test_hugging_face_model_arguments():
    assert model_args("org/model:Q1_0") == ["-hf", "org/model:Q1_0"]


def test_local_model_arguments():
    assert model_args("models/model.gguf") == ["-m", "models/model.gguf"]


def test_finds_project_local_executable(monkeypatch, tmp_path):
    executable = tmp_path / "llama-cli"
    executable.touch()
    monkeypatch.setenv("SLOTHBIT_LLAMA_CPP_DIR", str(tmp_path))
    monkeypatch.setattr("slothbit.llama.shutil.which", lambda name: None)

    assert find_executable("cli") == str(executable)


def test_cli_command(monkeypatch):
    monkeypatch.setattr("slothbit.llama.find_executable", lambda kind: "/bin/llama-cli")
    settings = Settings(threads=8, gpu_layers=10)

    command = build_cli_command(settings, "hello", predict=32)

    assert command[:3] == ["/bin/llama-cli", "-hf", settings.model]
    assert command[-4:] == ["--threads", "8", "--n-gpu-layers", "10"]


def test_server_command(monkeypatch):
    monkeypatch.setattr("slothbit.llama.find_executable", lambda kind: "/bin/llama-server")

    command = build_server_command(Settings(host="0.0.0.0", port=9000))

    assert command[:3] == ["/bin/llama-server", "-hf", Settings().model]
    assert command[3:5] == ["--host", "0.0.0.0"]
