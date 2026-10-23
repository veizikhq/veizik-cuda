# veizik-cuda 1.0.0 — Qwen3.5 / Qwen3.6 on NVIDIA GPUs, with a local OpenAI-compatible server

**Qwen3.5 (0.8B, 2B, 4B, 9B) and Qwen3.6-35B-A3B on your own NVIDIA GPU, on-device.** Veizik runs
the models through its own native CUDA engine — no Python runtime, no CUDA toolkit, no cloud at
inference time. You supply the weights; nothing leaves the machine.

- Package: `veizik-qwen-cuda-1.0.0-linux-x86_64.tar`  ·  SHA-256 `9deb3497b23f233a9bfabbff2dd1bfb10a60b316a5a361010f5ce41b40b880dd`  ·  CLI `1.2.0` (x86_64 build `9b000b81`, aarch64 build `af92fd50`)  ·  backend CUDA
- Supported: `qwen35_0p8b`, `qwen35_2b`, `qwen35_4b`, `qwen35_9b`, `qwen36_35b_a3b`  ·  Hardware: NVIDIA compute capability 8.0+ — `sm_80` / `sm_86` / `sm_89` / `sm_90a` / `sm_100a` / `sm_120a`
- GPU code ships as per-architecture **cubin (SASS)**; the loader does no JIT
- Install: `echo "9deb3497b23f233a9bfabbff2dd1bfb10a60b316a5a361010f5ce41b40b880dd  veizik-qwen-cuda-1.0.0-linux-x86_64.tar" | sha256sum -c - && tar xf veizik-qwen-cuda-1.0.0-linux-x86_64.tar && cd veizik-qwen-cuda-0.1.0-rc1-linux-x86_64-sm86 && ./install.sh`   (full guide: [README](README.md))
- Benchmarks: Veizik's own measured figures — [bench/REPRODUCIBILITY.md](bench/REPRODUCIBILITY.md)  (reproduce: [bench/repro_kit/](bench/repro_kit/))
- Licence: install + evaluation free; production use licensed. Terms: Veizik Terms of Service, "License & entitlement" (https://veizik.com/terms), and the Veizik distribution licence ([`LICENSE`](../LICENSE)) with the third-party notices ([`NOTICE.md`](../NOTICE.md)) at the root of this repository ([README](README.md) §6).
- Replaces: the withdrawn tarball `20681397a43d3a9093aa25517a1e61bc594d0a4df2a1a583189d914bf3d58c55` (same file name). Delete it and download again.

## Changed in this tarball (9deb3497, replaces the withdrawn 20681397)

- The launcher that opens the sealed engine was rebuilt with loader hardening against unprivileged
  extraction of the GPU code: it re-executes itself in a clean environment before it opens the GPU
  code, and checks its own integrity at run time — runtime anti-tamper aborts naive binary patches
  (a determined on-disk patch remains a known residual). The device key never leaves the device.
  Nothing you type or see changes.
- The engine and the per-architecture GPU code are byte-for-byte those of `20681397`, so its
  benchmark rows carry unchanged (they remain previous-version rows; see below).
- The activation flow, the model catalogue, the `veizik` command (CLI `1.2.0`) and the folder name
  are unchanged.

## Added

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

## Changed

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
- **`run` output.** `gen.txt` holds the generated text; the engine detokenizes (per the package's
  `INTERFACE.json`). If it holds whitespace-separated numbers instead, they are token ids: decode them
  with the tokenizer of the checkpoint you supplied. `serve` and `veizik chat` return text.
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
- **Benchmark rows are previous-version rows.** They were measured on the previous build (the
  LLM-only 1.0.0 build, 2026-10-21) with the same per-architecture GPU code, and were not re-measured
  on this tarball (`9deb3497`) or on the withdrawn `20681397`. Server throughput over HTTP is not published.
- **Architectures:** `sm_80`, `sm_90a` and `sm_100a` GPU code is included but was not run in
  validation.
- **WSL is not supported** for the sealed engine; use a native Linux host. The tarball also contains
  an aarch64 CLI binary, but the engine is x86-64 only, so the package installs on Linux x86-64 only.
- **Not in this release:** LoRA adapters, image or other multimodal input, tool/function calling,
  `logprobs` and embeddings over HTTP, a weight converter, downloading weights with `veizik pull`.
