# syntax=docker/dockerfile:1.7

ARG PYTHON_VERSION=3.12
ARG DEBIAN_VERSION=bookworm

FROM debian:${DEBIAN_VERSION}-slim AS llama-builder

ARG TARGETARCH
ARG LLAMA_CPP_REPOSITORY=https://github.com/PrismML-Eng/llama.cpp.git
ARG LLAMA_CPP_REF=bdc23b56b4458b9f1655aec5287f3ab56ee8daaa

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        ca-certificates \
        cmake \
        g++ \
        git \
        libssl-dev \
        ninja-build \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src/llama.cpp

RUN git init \
    && git remote add origin "${LLAMA_CPP_REPOSITORY}" \
    && git fetch --depth 1 origin "${LLAMA_CPP_REF}" \
    && git checkout --detach FETCH_HEAD

# A static CPU backend keeps the runtime image small and avoids backend-library
# discovery issues. KleidiAI provides optimized Arm kernels on Apple Silicon's
# Linux VM; PQ2_0 operations not covered by it use Prism's Arm implementation.
RUN if [ "${TARGETARCH}" = "arm64" ]; then kleidiai=ON; else kleidiai=OFF; fi \
    && cmake -S . -B build -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_SHARED_LIBS=OFF \
        -DGGML_BACKEND_DL=OFF \
        -DGGML_CPU_KLEIDIAI="${kleidiai}" \
        -DGGML_LLAMAFILE=OFF \
        -DGGML_NATIVE=OFF \
        -DLLAMA_BUILD_EXAMPLES=OFF \
        -DLLAMA_BUILD_SERVER=ON \
        -DLLAMA_BUILD_TESTS=OFF \
        -DLLAMA_BUILD_UI=OFF \
        -DLLAMA_OPENSSL=ON \
        -DLLAMA_USE_PREBUILT_UI=OFF \
    && cmake --build build --parallel --target llama-cli llama-server

FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION} AS python-builder

WORKDIR /src/slothbit
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels .

FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION} AS runtime

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        ca-certificates \
        libgomp1 \
        libssl3 \
        libstdc++6 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 slothbit \
    && useradd --uid 10001 --gid slothbit --create-home slothbit \
    && install -d -o slothbit -g slothbit /models

COPY --from=llama-builder /src/llama.cpp/build/bin/llama-cli /usr/local/bin/llama-cli
COPY --from=llama-builder /src/llama.cpp/build/bin/llama-server /usr/local/bin/llama-server
COPY --from=python-builder /wheels /wheels

RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels

ENV LLAMA_CACHE=/models \
    SLOTHBIT_CONTEXT_SIZE=4096 \
    SLOTHBIT_GPU_LAYERS=0 \
    SLOTHBIT_HOST=0.0.0.0 \
    SLOTHBIT_MODEL=prism-ml/Ternary-Bonsai-27B-gguf:PQ2_0 \
    SLOTHBIT_PORT=8080

VOLUME ["/models"]
EXPOSE 8080

USER slothbit
ENTRYPOINT ["slothbit"]
CMD ["--help"]
