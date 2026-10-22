# veizik-cuda — CUDA / Linux

On-device inference for NVIDIA GPUs (Linux x86_64) through veizik's own sealed native engine — no CUDA
toolkit, no Python, no PyTorch, no compiler on the host, just an NVIDIA driver. The engine runs only on
an **activated device**; GPU code ships encrypted at rest and is handed a device-bound key at
activation, and `bin/vzseal` self-checks integrity at every launch.

This repository is the CUDA/Linux release hub. Each package is self-contained and carries its own
`README.txt`; the full support documentation for a package lives under [`cuda_deploy/`](cuda_deploy/).

## Current release

**v1.0.0 (Qwen3.5 / Qwen3.6)** — one package serves **five** Qwen language models (the runtime selects
the model at run time):

| Model | Type | Status |
|---|---|---|
| Qwen3.5-0.8B · Qwen3.5-2B · Qwen3.5-4B · Qwen3.5-9B | dense | EXPERIMENTAL |
| Qwen3.6-35B-A3B | MoE (A3B active) | EXPERIMENTAL |

Target: NVIDIA per-arch cubin for **sm_80, sm_86, sm_89, sm_90a, sm_100a, sm_120a**, Linux x86_64.

- **File:** `veizik-qwen-cuda-1.0.0-linux-x86_64.tar`
- **Download:** https://github.com/veizikhq/veizik-cuda/releases/download/v1.0.0/veizik-qwen-cuda-1.0.0-linux-x86_64.tar
- **sha256:** `20681397a43d3a9093aa25517a1e61bc594d0a4df2a1a583189d914bf3d58c55` (see root [`SHA256SUMS`](SHA256SUMS))

## Install & run

Get the bundle from [Releases](https://github.com/veizikhq/veizik-cuda/releases), verify its `sha256`
against the root `SHA256SUMS`, then:

```bash
tar xf veizik-qwen-cuda-1.0.0-linux-x86_64.tar
cd veizik-qwen-cuda-0.1.0-rc1-linux-x86_64-sm86
./install.sh                 # installs `veizik`; verifies SHA-256 + the engine's own seal first
veizik activate              # bind this device (once) — browser, or --key/--password-stdin for headless
veizik run qwen36_35b_a3b "Explain attention in one paragraph."
```

Model weights are **not** bundled — point a run at each model's Hugging Face snapshot with
`--weights DIR`, the `VZ_WEIGHTS` variable, or your Hugging Face cache. The Qwen weights carry their
upstream Apache-2.0 license; the veizik engine is proprietary.

Serving: `veizik serve` exposes an OpenAI-compatible API (`/v1/chat/completions`, `/v1/completions`,
`/v1/models`) for all five models; `veizik chat` is an interactive terminal session.

## Documentation

- Each package's own `README.txt` — install, activation, weights, and run, inline in the bundle.
- [`cuda_deploy/`](cuda_deploy/) — complete CLI reference, every verb and flag, and reproducible
  own-measured benchmarks (golden data + repro kit).

Benchmark policy: the published board shows veizik's own absolute figures only (no competitor
comparison in customer-facing material); every number is reproducible from the committed repro kit.
