# Veizik CUDA — Usage guide

Scenario-level guidance: choosing a mode, memory, reproducibility, and what to do when something
fails. For the exhaustive flag list see [`CLI_USAGE.md`](CLI_USAGE.md).

---

## 1. Choosing a mode

| Mode | Use it when |
|---|---|
| `quality` | you want the result closest to the unquantized checkpoint; largest memory, slowest |
| `balanced` | **default.** The configuration every published speed number was measured with |
| `fast` | lower memory and faster than balanced, trading a little quality |
| `ultrafast` | lowest latency; same light quantization as `fast` |
| `low-memory` | smallest footprint; lowest quality. Use when VRAM is the binding constraint |

Modes are mapped explicitly — there is no unquantized default. If a family does not offer a mode,
asking for it is an error (exit `2`), not a silent substitution.

---

## 2. Memory

The resident footprint is set by the model and the mode, and the checkpoint you supply is loaded
from disk, not bundled. If a run exceeds VRAM it fails with a budget error rather than being killed
by the allocator.

Practical order of things to try when you are short on VRAM:
1. `--mode low-memory` (or `fast` if `low-memory` is unavailable for the family)
2. reduce `--width`/`--height` (image) or `--frames` (video)
3. reduce `--steps`
4. pick a smaller model in the family

---

## 3. Reproducibility

- Text: `--temperature 0` is greedy and deterministic. Any non-zero temperature, `--top-p` or
  `--top-k` makes the run non-deterministic and is **experimental** — outside the engine release
  contract.
- Image/video: fix `--seed`, `--steps`, `--mode` and the resolution. The same package on the same
  GPU architecture reproduces the same output.
- A different package build, mode, or GPU architecture may legitimately produce different bytes. If
  you need byte-stable outputs across time, pin the package SHA from `RELEASE_NOTES.md`.

---

## 4. Serving

Resident/batched serving is **not exposed in this release's CLI**. Each `veizik run` is a
self-contained process: it brings up the bundle, runs, and exits. If you are scripting many
generations, keep the process alive across prompts where your family's CLI supports it, or accept
per-run startup cost.

---

## 5. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| exit `70` | not activated on this device | `veizik activate` |
| exit `74` | lease not issued for this bundle/device | re-activate; do not copy an activated install between machines |
| exit `4` | bundle integrity failed, or sealed GPU modules did not open | reinstall from the tarball; verify the SHA first. Do not edit files inside the bundle |
| exit `3` | weights/tokenizer/prompt file missing | check `--weights`, `VZ_WEIGHTS`, and that the path is readable |
| exit `2` naming the GPU | GPU generation could not be read | check the driver with `veizik doctor`; confirm the GPU is compute capability 8.0+ |
| exit `2` on an option you expected to work | the option is refused in shipped bundles | see the "refused" table in `CLI_USAGE.md` |
| `--lora` ran but nothing changed | **LoRA is inert in this release** | do not rely on it; see §6 |
| anything under WSL | sealed bundles are not supported on WSL | use a native Linux host |

Always start with `veizik doctor` — it reports the runtime root, GPU, driver, bundle integrity and
lease state in one pass, and it is the fastest way to tell an environment problem from a usage one.

---

## 6. LoRA in this release

`--lora` / `--lora-scale` appear in some bundles' interfaces but **do not apply a LoRA in this
release**. A run using them exits `0` and produces a normal-looking, unmodified result — it fails
silently. **Do not rely on `--lora`.**

Working LoRA support is in active development and will ship in a later update. Until then treat
these flags as present-but-inert. For WAN specifically, the shipped package is accompanied by a LoRA
note stating this prominently; read it before using those flags.

---

## 7. What Veizik does not do

- It does not download model weights for you.
- It does not make network calls at inference time.
- It does not upload prompts, outputs, or telemetry.
- It does not change the licence of the checkpoint you supply.
