# veizik-cuda 1.1.0 — Qwen3.5 / Qwen3.6 on NVIDIA GPUs, with image and video input on Qwen3.6-35B-A3B

**Qwen3.5 (0.8B, 2B, 4B, 9B) and Qwen3.6-35B-A3B on your own NVIDIA GPU, on-device.** Veizik runs
the models through its own native CUDA engine — no Python runtime, no CUDA toolkit, no cloud at
inference time. You supply the weights; nothing leaves the machine.

- Package: `veizik-qwen-cuda-1.1.0-linux-x86_64.tar`  ·  SHA-256 `d38f30780b873bac616b5b1e7e54a47ee6e8c9dcb5ad18fe47d86a6457852a54`  ·  58,573,312 B  ·  CLI `1.2.0` (x86_64 build `9b000b81`, aarch64 build `af92fd50`)  ·  backend CUDA
- Supported: `qwen35_0p8b`, `qwen35_2b`, `qwen35_4b`, `qwen35_9b`, `qwen36_35b_a3b`  ·  Hardware: NVIDIA compute capability 8.0+ — `sm_80` / `sm_86` / `sm_89` / `sm_90a` / `sm_100a` / `sm_120a`
- GPU code ships as per-architecture **cubin (SASS)**; the loader does no JIT
- Install: `echo "d38f30780b873bac616b5b1e7e54a47ee6e8c9dcb5ad18fe47d86a6457852a54  veizik-qwen-cuda-1.1.0-linux-x86_64.tar" | sha256sum -c - && tar xf veizik-qwen-cuda-1.1.0-linux-x86_64.tar && cd veizik-qwen-cuda-0.1.0-rc1-linux-x86_64-sm86 && ./install.sh`   (full guide: [README](README.md))
- Benchmarks: Veizik's own measured figures — [bench/REPRODUCIBILITY.md](bench/REPRODUCIBILITY.md)  (reproduce: [bench/repro_kit/](bench/repro_kit/))
- Licence: install + evaluation free; production use licensed. Terms: Veizik Terms of Service, "License & entitlement" (https://veizik.com/terms), and the Veizik distribution licence ([`LICENSE`](../LICENSE)) with the third-party notices ([`NOTICE.md`](../NOTICE.md)) at the root of this repository ([README](README.md) §6).
- Supersedes: `veizik-cuda 1.0.0`.

## 1.1.0 — Added

- **Image input on Qwen3.6-35B-A3B:** `--image FILE --prompt …` on the package's launcher (`PIPELINE.sh`) — one PNG or
  JPEG per run, with `--prompt` or `--prompt-file`. The chat template is applied and the answer ends at
  the end-of-turn token. `--image-max-pixels N` (default 1,048,576) bounds the pixel count after
  resizing; a larger image is scaled down to fit.
- **Video input on Qwen3.6-35B-A3B:** `--video DIR --prompt …` on the package's launcher — a folder of
  2 to 256 PNG or JPEG frames, all the same size, in file-name order; one video per run, not together
  with `--image`. `--video-fps X` (default 2) sets the time stamps between frames;
  `--video-max-pixels N` (default 262,144) bounds every frame's pixel count after resizing.
- GPU code for the image and video stage for `sm_86`, `sm_89` and `sm_120a`. On a GPU the stage does
  not support, the run is refused cleanly with code 50 before any image or video work.
- New exit-code meanings for image and video runs: `2` for an unusable request or input (wrong model,
  more than one input, no text prompt, an unsupported or damaged file, frames of different sizes or
  outside 2–256, or over the size or aspect-ratio budget); `3` for an image file
  or frames folder that is missing or unreadable.

## 1.1.0 — Unchanged

- The five text models, their modes, `veizik chat`, `veizik serve` (text only) and the `veizik`
  command (CLI `1.2.0`, x86_64 build `9b000b81`). Activation works as in 1.0.0.
- Image and video input is not available through `veizik chat` or `veizik serve`, nor on the four
  Qwen3.5 models.

## History

- 1.0.0 (2026-10-23): first CUDA Qwen package. It was re-issued once with a hardened loader as
  `9deb3497…`, replacing the withdrawn `20681397…`; engine and GPU code were unchanged by that re-issue.

The sections below describe 1.0.0; everything in them still applies to 1.1.0.

## 1.0.0 — Added

- `veizik serve <model>`: a resident, batched, OpenAI-compatible HTTP server on `127.0.0.1` —
  `POST /v1/chat/completions`, `POST /v1/completions`, `GET /v1/models`, server-sent-event streaming
  (with optional `stream_options.include_usage`), `GET /health`, `/healthz`, `/readyz` and
  `/metrics`. **Chat completions are supported for all five models** (the shipped signed model
  catalogue declares chat capability for each). The model loads once; requests are batched across
  generation slots. Validated with concurrent requests on the dense models and on Qwen3.6-35B-A3B.
- `veizik chat <model>`: an interactive terminal session for all five models — type a message, read
  the model's text reply, repeat (`/help`, `/clear`, `/stats`, `/model`, `/exit`).
- **API-key authentication for the CUDA server:** `veizik serve <model> --require-auth (--api-key K |
  --keyfile F)`. Requests without the key, or with a wrong one, answer HTTP 401 (`invalid_api_key`,
  `WWW-Authenticate: Bearer`); `Authorization: Bearer <key>` answers 200. It covers
  `/v1/chat/completions`, `/v1/completions` and `/v1/models`; the probe endpoints `/health`,
  `/healthz` and `/readyz` stay open. `--keyfile` is recommended: `--api-key` puts the key on the
  CLI's command line.
- `veizik run` for the five models with five modes (`quality`, `balanced`, `fast`, `ultrafast`,
  `low-memory`), prompt from text, file, or token ids, and opt-in experimental sampling.
- Per-architecture native GPU code for `sm_80` through `sm_120a`.
- Device-bound activation, per device rather than per model: browser approval, or browser-free
  activation with an account key and CLI password (`activate --key … --password-stdin`);
  `deactivate [--forget]` to release a machine; silent lease renewal on approved machines.
- A reproducibility kit and committed results: pinned prompt and SHA manifest, the grid and
  extraction scripts, and per-GPU rows for RTX 3090, RTX 4090 and RTX 5090.

## 1.0.0 — Changed

- GPU modules ship as per-architecture cubin for every supported architecture, including the
  consumer ones. Earlier internal builds shipped PTX text for some consumer architectures; that form
  is superseded.
- Bundle integrity is checked at every start; a modified bundle stops with exit `4` instead of
  running degraded.

## Known issues and limits

- **The CUDA server is loopback-only.** `--host` accepts only `127.0.0.1` or `localhost`; a
  non-loopback address is refused (exit 2). To serve other machines, put a reverse proxy that
  terminates TLS in front of it and forwards to the loopback port. Without `--require-auth` the
  server has no authentication (any local process can use it). Authentication is one shared key per
  server process, not per-user keys.
- **No usage ledger or quotas in the CUDA server.** `serve --usage-log` and `--quota-*` are accepted
  but not applied, and `--max-tokens` is accepted but not applied (set `max_tokens` per request);
  `keys`, `usage`, `audit` and `quota` are local CLI tools that the CUDA server does not read.
- **Stopping a detached server:** `veizik stop` does not see the CUDA server. If you started it in
  the background, stop it by signalling the engine process (find it with `ss -ltnp` on the port).
- **`run` output.** `veizik run` writes its output to `gen.txt` in `--out`; for text use `veizik chat`
  or `veizik serve`.
- **Chat sessions.** `veizik chat` is an interactive terminal session for all five models; each
  message is answered on its own (the CLI session keeps no conversation history between messages).
  `veizik serve` with `POST /v1/chat/completions` is the programmatic chat path; both return text.
- **Other CLI verbs on this package.** `veizik pull` is the CLI's downloader and reports that it
  cannot fetch weights for this package (download the Hugging Face snapshots yourself).
  `veizik convert` is a checkpoint checker: this release ships no converter and it writes no file.
  `veizik inspect` shows a model's catalogue status and whether it can run here (it reports the
  external weights as missing). `veizik models` lists the five models; its `incomplete (no weights)`
  label is a per-model status, not a broken command. There is no `device-id` command: use
  `veizik devices`. `keys`, `usage`, `audit`, `quota` and `gateway` are real local CLI tools, not
  integrated with the CUDA server (`gateway` was not exercised against it in this release's
  validation).
- **Qwen3.6-35B-A3B `quality` mode** needs about 26 GB or more and did not complete on a 32 GB RTX
  5090 in validation; use `balanced` or `fast`. Serving Qwen3.6-35B-A3B used 27.1 GB of a 32 GB card.
- **Sampling is experimental** on `run` (`--temperature`, `--top-p`, `--top-k`, `--seed`); greedy
  decoding is the verified path.
- **Server context window:** 4,096 tokens per request (prompt plus generated) in the validated
  configuration.
- **Benchmark rows were measured on 1.0.0 builds** (2026-10-21, text input) and were not re-measured
  on 1.1.0. No figure is published for image or video input. Server throughput over HTTP is not published.
- **Architectures:** `sm_80`, `sm_90a` and `sm_100a` GPU code is included but was not run in
  validation.
- **WSL is not supported** for the sealed engine; use a native Linux host. The tarball also contains
  an aarch64 CLI binary, but the engine is x86-64 only, so the package installs on Linux x86-64 only.
- **Not in this release:** LoRA adapters, image or video input on the Qwen3.5 models or through
  `chat` / `serve`, audio input, tool/function calling,
  `logprobs` and embeddings over HTTP, a weight converter, downloading weights with `veizik pull`.
