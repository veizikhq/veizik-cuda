# Veizik on CUDA / Linux — Deployment & Support

Veizik runs quantized diffusion, video and language models **on your own GPU** through its own
native engine: CUDA kernels emitted by the Veizik compiler, no Python, no PyTorch, no cloud at
inference time. This folder is the authoritative support documentation for the shipped CUDA builds —
install, activation, every CLI command, and a reproducible benchmark set.

> **Scope.** This covers the CUDA/Linux packages. The Apple-Silicon (`veizik-metal`) deployment is a
> separate package. Both are architecture targets of the same shared core, not forks.

---

## 1. What ships

CUDA ships **one package per model family**. Each package is a sealed, device-bound bundle.

| Family | Package | Models | Task |
|---|---|---|---|
| Qwen | `veizik-qwen-cuda-<ver>-linux-x86_64-<arch>` | Qwen3.5 0.8B / 2B / 4B / 9B, Qwen3.6-35B-A3B | text generation |
| FLUX.1 | `veizik-flux-<ver>-linux-x86_64` | FLUX.1 key set | text-to-image |
| SD3.5 | `veizik-sd35-<ver>-linux-x86_64` | SD3.5 Medium, SD3.5 Large | text-to-image |
| WAN | `veizik-wan-<ver>-linux-x86_64` | Wan2.1-T2V-1.3B | text-to-video |

| Item | Value |
|---|---|
| Package SHA-256 | per release — see `RELEASE_NOTES.md` for the shipped value |
| CLI version (`veizik version`) | see `RELEASE_NOTES.md` |
| Backend | `CUDA` (native kernels, per-architecture) |
| GPU code form | per-architecture **cubin (SASS)**; the loader does no JIT |
| Architectures | sm_80 / sm_86 / sm_89 / sm_90a / sm_100a / sm_120a |
| Sealing | engine and GPU modules are sealed; integrity is checked at every boot |
| Activation | device-bound lease (see §4) |
| Model weights | **not included** — you supply the checkpoint (see §3) |

**Weights are yours.** The package contains the engine, not the model. You point Veizik at a
checkpoint you already have the right to use. Nothing is uploaded.

---

## 2. Install

1. Unpack the release tarball and verify it first:
   ```bash
   sha256sum veizik-<family>-<ver>-linux-x86_64.tar
   # compare against the value published in RELEASE_NOTES.md
   tar xf veizik-<family>-<ver>-linux-x86_64.tar
   ```
2. Run the installer from the unpacked directory:
   ```bash
   ./install.sh
   ```
   It places the `veizik` command (and the short alias `vz`) on your `PATH` and records the runtime
   root.
3. Confirm the install:
   ```bash
   veizik version      # → CLI version, backend CUDA
   veizik doctor       # → runtime, GPU, driver, bundle integrity, lease
   ```

If the CLI reports that it cannot find the runtime, point it at the install root:
```bash
export VEIZIK_ROOT=/path/to/unpacked/veizik-<family>-<ver>-linux-x86_64
veizik doctor
```

### System requirements
- NVIDIA GPU, compute capability **8.0 or newer** (Ampere, Ada, Hopper, Blackwell).
- Linux x86-64 with a driver matching your GPU generation. `veizik doctor` reports the driver it sees
  and refuses rather than guessing if the GPU generation cannot be read.
- Free VRAM ≥ the model's resident footprint for the selected mode. `--mode low-memory` (where the
  family offers it) is the smallest footprint; `quality` is the largest.
- Disk space for the checkpoint you supply, which is usually far larger than the package.

> **WSL is not a supported runtime for the sealed bundles.** Use a native Linux host.

---

## 3. Supply the model weights

Veizik reads the checkpoint you already have — it does not download one for you and does not ship one.

```bash
# explicit
veizik run <model> --weights /path/to/checkpoint --prompt "..." --out ./out

# or set a search root once
export VZ_WEIGHTS=/data/checkpoints
```
Without `--weights`, Veizik searches `VZ_WEIGHTS`, `VEIZIK_CACHE`, and the Hugging Face cache, in
that order. If no checkpoint is found the run stops with exit code **3** and names what is missing.

You are responsible for holding a licence to the weights you use. Several upstream checkpoints are
released under non-commercial terms; Veizik does not change those terms.

---

## 4. Activate (once per device)

Activation binds the install to **this machine**. It is per device, not per model, and it is a
lease — not a transfer.

```bash
veizik activate            # binds this device
veizik status              # shows lease state and expiry
veizik device-id           # the identifier the lease is bound to
```

What not to do: do not invoke the activation helper binary by hand, and do not copy an activated
install to another machine — the lease will not verify there.

| Exit code | Meaning |
|---|---|
| `70` | activation required — no device key, lease or key blob; run `veizik activate` |
| `74` | entitlement refused — a lease is present but was not issued for this bundle on this device |

---

## 5. Quick start

```bash
veizik run qwen35_2b   --prompt "Explain attention in two sentences." --out ./out
veizik run sd35large   --prompt "A red colored car." --steps 28 --out ./out
veizik run flux1dev    --prompt "A lighthouse at dusk." --steps 28 --out ./out
veizik run wan21_t2v_1_3b --prompt "A paper boat drifting downstream." --out ./out
veizik doctor
```
Add `--mode quality|balanced|fast|ultrafast|low-memory` to trade quality against memory and speed.
`balanced` is the default and is the configuration every published speed number was measured with.

---

## 6. Benchmarks & reproducibility

Measured numbers, the exact commands that produced them, and the pinned inputs live in
[`bench/REPRODUCIBILITY.md`](bench/REPRODUCIBILITY.md) with the input set under
[`bench/repro_kit/`](bench/repro_kit/).

**We publish our own numbers only.** Each figure names the GPU, the mode, the resolution or token
count, and the exact package it was measured on. We do not publish comparisons against other
engines, and we do not publish a number we have not measured on the shipped bytes.

---

## 7. Current limitations

Stated plainly, because they affect what you can do today:

- **LoRA is not available in this release.** Working LoRA support is in development. Where a LoRA
  option appears in a bundle's interface it is **present but inert** — see the family's
  `RELEASE_NOTES.md` and, for WAN, the LoRA note shipped alongside the package.
- **No weight converter ships yet.** Bring a checkpoint in a format the family's loader accepts.
- Per-family scope limits (resolution, frame count, task) are listed in `RELEASE_NOTES.md`.

---

## 8. Pointers

| Topic | Where |
|---|---|
| Every command and flag | [`CLI_USAGE.md`](CLI_USAGE.md) |
| Run modes, serving, troubleshooting | [`USAGE_GUIDE.md`](USAGE_GUIDE.md) |
| Measured data + how to reproduce | [`bench/REPRODUCIBILITY.md`](bench/REPRODUCIBILITY.md) |
| This release's contents and SHAs | [`RELEASE_NOTES.md`](RELEASE_NOTES.md) |
| What `doctor` asserts | `veizik doctor --explain` |
