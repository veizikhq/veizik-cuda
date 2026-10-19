# veizik-cuda — CUDA / Linux

On-device inference for NVIDIA GPUs (Linux x86_64) through veizik's own sealed native engine — no CUDA
toolkit, no Python, no PyTorch, no compiler on the host, just an NVIDIA driver. The engine runs only on
an **activated device**; GPU kernels ship encrypted at rest and are handed a device-bound key at
activation, and `bin/vzseal` self-checks integrity at every launch.

This repository is the CUDA/Linux release hub. Each package is self-contained and carries its own
`README.txt`; the full support documentation for a package lives under [`cuda_deploy/`](cuda_deploy/).

## Current release

**v1.0.0 (Qwen3.5 / Qwen3.6)** — one package serves **five** Qwen language models (the runtime selects
the model at run time; per-family single sealed inner):

| Model | Type | Status |
|---|---|---|
| Qwen3.5-0.8B · Qwen3.5-2B · Qwen3.5-4B · Qwen3.5-9B | dense | EXPERIMENTAL |
| Qwen3.6-35B-A3B | MoE (A3B active) | EXPERIMENTAL |

Target: CUDA compute capability **8.6 (sm_86)**, Linux x86_64.

## Install & run

Get the bundle from [Releases](https://github.com/veizikhq/veizik-cuda/releases), verify its `sha256`,
then:

```bash
tar xf veizik-qwen-cuda-0.1.0-rc1-linux-x86_64-sm86.tar
cd veizik-qwen-cuda-0.1.0-rc1-linux-x86_64-sm86
./install.sh                 # installs `veizik`; verifies SHA-256 + the engine's own seal first
veizik activate              # bind this device (once) — browser, or --key/--password-stdin for headless
veizik run qwen3.6-35b-a3b "Explain attention in one paragraph."
```

Model weights are **not** bundled — point a run at each model's Hugging Face snapshot with
`--weights DIR`, the `VZ_WEIGHTS` variable, or your Hugging Face cache. The Qwen weights carry their
upstream Apache-2.0 license; the veizik engine is proprietary.

## Documentation

- Each package's own `README.txt` — install, activation, weights, and run, inline in the bundle.
- [`cuda_deploy/`](cuda_deploy/) — complete CLI reference, every verb and flag, and reproducible
  own-measured benchmarks (golden data + repro kit). *(Being populated for v1.0.0.)*

Benchmark policy: the published board shows veizik's own absolute figures only (no competitor
comparison in customer-facing material); every number is reproducible from the committed repro kit.
