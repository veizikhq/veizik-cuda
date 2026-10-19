# Veizik CUDA — CLI reference

Every command and flag of the shipped CUDA CLI. `vz` is an alias for `veizik`. Built-in help:

```bash
veizik --help          # verbs
veizik <verb> --help   # flags for one verb
veizik version         # CLI version + backend
veizik doctor          # environment, GPU, bundle integrity, lease
```

Unknown or mistyped options are **errors, never ignored** — the run stops with exit code `2`.

---

## Verbs

| Verb | What it does |
|---|---|
| `run` | generate with a model |
| `activate` | bind this device (once per machine) |
| `status` | lease state and expiry |
| `device-id` | the identifier the lease binds to |
| `doctor` | environment + integrity checks |
| `version` | CLI version and backend |

---

## `veizik run <model> [flags]`

### Common to every family

| Flag | Type | Default | Notes |
|---|---|---|---|
| `--prompt TEXT` | string | — | exclusive with `--prompt-file`; visible in the process list |
| `--prompt-file PATH` | path | — | UTF-8 file; prefer this for long or sensitive prompts |
| `--out DIR` | path | — | output directory, created if missing; **must be outside the bundle** |
| `--mode NAME` | enum | `balanced` | `quality` · `balanced` · `fast` · `ultrafast` · `low-memory` (availability varies by family) |
| `--weights PATH` | path | search | checkpoint directory; without it `VZ_WEIGHTS`, `VEIZIK_CACHE` and the HF cache are searched |
| `--seed N` | int | family default | reproducibility |
| `--steps N` | int | family default | denoise steps (image/video) or tokens (text) |

### Text (Qwen)

| Flag | Type | Range / default | Notes |
|---|---|---|---|
| `--tokens N` | int | 1–4096, default 128 | same meaning as `--steps`; some CLI releases accept only `--steps` |
| `--ids-file PATH` | path | — | token ids instead of text; exclusive with `--prompt`/`--prompt-file` |
| `--temperature X` | decimal | 0–2, default 0 | `0` is greedy and deterministic. Sampling is **experimental** |
| `--top-p X` | decimal | 0–1 | nucleus sampling (experimental) |
| `--top-k N` | int | 0–1000 | top-k sampling (experimental) |

Outputs: `gen.txt` (generated token ids, whitespace separated) and `logits_last.bin` (float32 logits
of the last prompt position).

> **The text engine has no detokenizer in this release** — it emits token ids. Decode them with the
> tokenizer of the checkpoint you supplied.

### Image (FLUX.1, SD3.5)

| Flag | Type | Notes |
|---|---|---|
| `--neg TEXT` / `--negative TEXT` | string | negative prompt |
| `--width N` / `--height N` | int | output resolution; family-dependent valid set |
| `--guidance X` | decimal | classifier-free guidance scale |
| `--model NAME` | string | select the model inside a multi-model family package |

### Video (WAN)

| Flag | Type | Notes |
|---|---|---|
| `--frames N` | int | frame count |
| `--width N` / `--height N` | int | frame size |
| `--shift X` | decimal | schedule shift |
| `--guidance X` / `--guidance2 X` | decimal | guidance (second value for two-expert models) |
| `--image PATH` | path | image conditioning, where the model supports it |
| `--extend` | flag | extend an existing clip, where supported |

### Options that are refused in the shipped bundles

These exist in the interface but are disabled; using them stops the run rather than silently
degrading:

| Flag | Behaviour |
|---|---|
| `--lora FILE` / `--lora-scale X` | **present but inert in this release** — see `RELEASE_NOTES.md` and the WAN LoRA note. A run using them exits 0 and produces an unmodified result |
| `--wcache DIR` | refused — internal, disabled in shipped bundles |
| `--lora2` | refused — not supported |

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | ok |
| `1` | engine failure, or the engine did not report its bits-per-weight line |
| `2` | usage: unknown/mistyped option, value out of range, unknown model or mode, `--out` inside the bundle, or the GPU generation could not be read |
| `3` | an input is missing or unreadable: weights, tokenizer, prompt file, or the output folder cannot be created |
| `4` | the bundle could not be brought up — integrity check failed (a file was changed, added or removed: reinstall) or the sealed GPU modules did not open |
| `70` | activation required — run `veizik activate` |
| `74` | entitlement refused — the lease was not issued for this bundle on this device |

---

## Environment variables

| Variable | Effect |
|---|---|
| `VEIZIK_ROOT` | install root, if the CLI cannot find the runtime |
| `VZ_WEIGHTS` | checkpoint search root |
| `VEIZIK_CACHE` | secondary checkpoint cache |

Veizik does not read credentials from the environment and does not make network calls at inference
time.
