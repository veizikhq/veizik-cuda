# Veizik CUDA 1.0.0 — first CUDA/Linux release

**Diffusion, video and language models on your own NVIDIA GPU, on-device.** Veizik runs quantized
checkpoints through its own native CUDA engine — no Python, no PyTorch, no cloud at inference time.
You supply the weights; nothing leaves the machine.

- Package: per family, see the table below · CLI `<ver>` · backend CUDA
- Supported hardware: compute capability **8.0+** — sm_80 / sm_86 / sm_89 / sm_90a / sm_100a / sm_120a
- GPU code ships as per-architecture **cubin (SASS)**; the loader does no JIT
- Install: `tar xf <package>.tar && ./install.sh` (full guide: [README](README.md))
- Benchmarks: veizik's own measured figures — [bench/REPRODUCIBILITY.md](bench/REPRODUCIBILITY.md)
  (reproduce: [bench/repro_kit/](bench/repro_kit/))
- Licence: install + evaluation free; production use licensed. See EULA.

## Packages in this release

| Family | Package | SHA-256 | Models |
|---|---|---|---|
| Qwen | `veizik-qwen-cuda-<ver>-linux-x86_64-<arch>.tar` | _pending — filled from the shipped bytes_ | Qwen3.5 0.8B / 2B / 4B / 9B, Qwen3.6-35B-A3B |
| FLUX.1 | `veizik-flux-<ver>-linux-x86_64.tar` | _pending_ | FLUX.1 key set |
| SD3.5 | `veizik-sd35-<ver>-linux-x86_64.tar` | _pending_ | SD3.5 Medium, SD3.5 Large |
| WAN | `veizik-wan-<ver>-linux-x86_64.tar` | _pending_ | Wan2.1-T2V-1.3B |

> A SHA is written here only after it is read from the package being shipped. A pending cell means
> that family has not shipped in this release.

## Added
- First CUDA/Linux packages for the Qwen, FLUX.1, SD3.5 and WAN families.
- Per-architecture native GPU code for sm_80 through sm_120a.
- Device-bound activation (`veizik activate`), per device rather than per model.
- Reproducibility kit: pinned prompts, seeds and input manifest per measured row.

## Changed
- GPU modules ship as per-architecture cubin. Earlier internal builds shipped PTX text for some
  consumer architectures; that form is superseded.

## Fixed
- Bundle integrity is checked at every boot; a modified bundle stops with exit `4` instead of
  running degraded.

## Known issues
- **LoRA is not functional in this release.** `--lora` / `--lora-scale` are **present but inert**
  where they appear: a run using them exits `0` and produces an unmodified result — it fails
  silently. Do not rely on them. Working LoRA support is in development for a later update. The WAN
  package ships a dedicated LoRA note stating this prominently.
- **The text engine has no detokenizer.** Qwen runs emit token ids (`gen.txt`); decode them with the
  tokenizer of the checkpoint you supplied.
- **Resident/batched serving is not exposed in this release's CLI.** Each run is a self-contained
  process.
- **No weight converter ships yet.** Bring a checkpoint in a format the family's loader accepts.
- **WSL is not supported** for the sealed bundles; use a native Linux host.
