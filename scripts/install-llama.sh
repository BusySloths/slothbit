#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="${SLOTHBIT_LLAMA_CPP_DIR:-${repo_root}/.tools/llama.cpp}"
repository="${LLAMA_CPP_REPOSITORY:-https://github.com/PrismML-Eng/llama.cpp.git}"
revision="${LLAMA_CPP_REF:-bdc23b56b4458b9f1655aec5287f3ab56ee8daaa}"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "error: this installer targets macOS (Darwin)" >&2
  exit 1
fi

for command in cmake git ninja; do
  if ! command -v "${command}" >/dev/null 2>&1; then
    echo "error: ${command} is required (install Xcode Command Line Tools and CMake)" >&2
    exit 1
  fi
done

if [[ -e "${target}" && ! -d "${target}/.git" ]]; then
  echo "error: ${target} exists but is not a git checkout; move it aside and retry" >&2
  exit 1
fi

mkdir -p "$(dirname "${target}")"
if [[ ! -d "${target}/.git" ]]; then
  git clone "${repository}" "${target}"
fi

git -C "${target}" fetch --depth 1 origin "${revision}"
git -C "${target}" checkout --detach FETCH_HEAD

build_dir="${target}/build"
cmake -S "${target}" -B "${build_dir}" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DGGML_METAL=ON \
  -DGGML_NATIVE=ON \
  -DGGML_CPU_KLEIDIAI=ON \
  -DGGML_LLAMAFILE=OFF \
  -DLLAMA_BUILD_EXAMPLES=ON \
  -DLLAMA_BUILD_SERVER=ON \
  -DLLAMA_BUILD_TESTS=OFF \
  -DLLAMA_BUILD_TOOLS=ON
cmake --build "${build_dir}" --config Release --target llama-cli llama-server

for executable in llama-cli llama-server; do
  binary="${build_dir}/bin/${executable}"
  if [[ ! -x "${binary}" ]]; then
    echo "error: expected ${binary} after build" >&2
    exit 1
  fi
  ln -sfn "build/bin/${executable}" "${target}/${executable}"
done

echo "Installed llama.cpp ${revision} in ${target}"
