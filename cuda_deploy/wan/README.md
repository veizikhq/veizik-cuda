# veizik-wan 1.2.0 (Wan2.1 / Wan2.2) — Usage Guide

Veizik renders text-to-video and image-to-video with the Wan2.1 and Wan2.2 models **on your own
NVIDIA GPU** through its own native engine: per-architecture GPU code, no Python, no framework, no CUDA
toolkit, no cloud at render time. This guide covers the WAN package; it is drawn from the files the
package itself carries (`README.txt`, `STAGES.txt`, `INTERFACE.json`, `CONFORMANCE.json`, `REPRO.md`),
which remain the authority for their bundle. Every option, default, mode, input, output and exit code
is also listed machine-readably in the package's `INTERFACE.json` (schema `vz_interface/1`).

The Qwen language package has its own guide: [`../README.md`](../README.md).

---

## 1. What ships

| Item | Value |
|---|---|
| Release | `v1.2.0` — veizik-wan 1.2.0 |
| Package | `veizik-wan-1.2.0-linux-x86_64.tar` |
| Package SHA-256 | `8a594e6587db6259175936d60e1604a2156d4835e72dcc458dcc685783e8b027` |
| Size | 7,112,192 B, 172 files |
| Host | Linux x86-64 with an NVIDIA GPU and its driver (`libcuda.so.1`). No Python, no framework, no CUDA toolkit |
| GPU code | precompiled kernel sets, sealed at rest: a base set for `sm_86` / `sm_89`, and separate sets for `sm_80`, `sm_90a`, `sm_100a` and `sm_120a`. The launcher picks the set for the GPU it finds |
| Activation | required — the kernels open only on a device activated for this release |
| Model weights | **not included** — you download the published checkpoints (§3) |

Models (pass the **model key** to `./veizik run`):

| model key | model | Hugging Face repository | task | experts | defaults: size · frames · steps · guidance · shift |
|---|---|---|---|---|---|
| `wan21_t2v_1_3b` | Wan2.1-T2V-1.3B | `Wan-AI/Wan2.1-T2V-1.3B-Diffusers` | text to video | 1 | 832×480 · 49 · 30 · 5.0 · 3.0 |
| `wan21_t2v_14b` | Wan2.1-T2V-14B | `Wan-AI/Wan2.1-T2V-14B-Diffusers` | text to video | 1 | 832×480 · 49 · 30 · 5.0 · 3.0 |
| `wan22_t2v_a14b` | Wan2.2-T2V-A14B | `Wan-AI/Wan2.2-T2V-A14B-Diffusers` | text to video | 2 | 1280×720 · 81 · 40 · 4.0 / 3.0 · by resolution |
| `wan22_i2v_a14b` | Wan2.2-I2V-A14B | `Wan-AI/Wan2.2-I2V-A14B-Diffusers` | image to video | 2 | 832×480 · 81 · 40 · 3.5 / 3.5 · by resolution |

The default seed is 42 for every model. On the two-expert models `--guidance` applies to the
high-noise expert and `--guidance2` to the low-noise expert. When `--shift` is not given, the flow
shift follows the model's per-resolution preset:

| model | 1280×720 / 720×1280 | 832×480 / 480×832 | other sizes |
|---|---|---|---|
| `wan22_t2v_a14b` | 12.0 | 8.0 | 3.0 |
| `wan22_i2v_a14b` | 5.0 | 3.0 | 3.0 |
| `wan21_*` | 3.0 | 3.0 | 3.0 |


---

## 2. Install and activate

```bash
curl -LO https://github.com/veizikhq/veizik-cuda/releases/download/v1.2.0/veizik-wan-1.2.0-linux-x86_64.tar
echo "8a594e6587db6259175936d60e1604a2156d4835e72dcc458dcc685783e8b027  veizik-wan-1.2.0-linux-x86_64.tar" | sha256sum -c -
# must print: veizik-wan-1.2.0-linux-x86_64.tar: OK
tar xf veizik-wan-1.2.0-linux-x86_64.tar
cd veizik-wan-1.2.0-linux-x86_64
bin/vzseal "$PWD"        # integrity check by hand: prints VZSEAL OK <n>, exit 0
```

The package runs from the folder you unpacked; it has no installer. Do not add, remove or edit files
inside that folder, and write output elsewhere (§4).

**Activation.** The GPU kernels open only on a device activated for this release.
Activating a device for the WAN package: the WAN package carries no activation tool of its own, so contact support@veizik.com to activate a device for it. Activation does not need the model weights; rendering does.
Without activation every GPU stage stops before any compute with
`VZ_PTX_BOOT_FAIL render rc <n>`, and the run exits **70** with `VZ_ACTIVATION_REQUIRED`:

| rc in the message | meaning |
|---|---|
| `-9` | no device key |
| `-13` | the licence is for another device or release, or has expired |
| `-16` | the key material is for another release |

A licence may enable only some features. A run the licence does not enable stops before any compute
with `VZ_ENT_REFUSED render rc -30` (or `-31` for a malformed licence policy) and exits **74** with
`VZ_ENTITLEMENT_REFUSED`. The check judges what the run actually loads and selects (the transformer
weights, the compute path, stream use), not what a caller claims.

---

## 3. Model weights

Download each model's Hugging Face snapshot from its publisher, under the publisher's licence, and
point the run at it with `--weights DIR` or `VZ_WEIGHTS=DIR`. Without either the run stops with exit 3.

| model | folders the weights directory must hold |
|---|---|
| `wan21_t2v_1_3b`, `wan21_t2v_14b` | `transformer/` `text_encoder/` `tokenizer/` `vae/` |
| `wan22_t2v_a14b` | `transformer/` (high-noise expert) `transformer_2/` (low-noise expert) `text_encoder/` `tokenizer/` `vae/` |
| `wan22_i2v_a14b` | as `wan22_t2v_a14b`, plus `vae_diffusers/` (the original VAE safetensors, read by the image encoder) |

- The transformers and the text encoder are read as published in F32 safetensors. A BF16 shard is
  refused by name. For `wan22_t2v_a14b`, `text_encoder/` may be the F32 umT5-XXL text encoder of
  `Wan-AI/Wan2.1-T2V-14B-Diffusers`; the A14B repository's BF16 encoder is its exact rounded copy.
- `vae/` is the prepared decoder layout, described by `vae/manifest.txt`.
  The package does not include a tool that prepares this `vae/` layout from the published checkpoint; contact support@veizik.com for the prepared decoder files before your first render.

```bash
export VZ_WEIGHTS=/data/models/Wan2.1-T2V-1.3B
./veizik run wan21_t2v_1_3b --out ~/wan-out --prompt-file prompt.txt
```

---

## 4. Run

```
./veizik run <model> --out DIR [--prompt TEXT | --prompt-file FILE] [--neg TEXT | --neg-file FILE]
             [--steps N] [--frames N] [--width W] [--height H] [--guidance G] [--guidance2 G2]
             [--seed N] [--shift S] [--mode quality|balanced|fast|ultrafast] [--resume yes]
             [--weights DIR] [--image FILE] [--extend DIR] [--stream yes --window-frames 81 --story FILE ...]
```

- Every option accepts `--key value` and `--key=value`; yes/no switches also take `true`/`false`,
  `on`/`off`, `1`/`0`. An unknown or mistyped option is an error (exit 2), never ignored.
- `--out DIR` must be **outside** the package folder; it is created if missing. Pass it every time
  (its default, `$PWD/veizik-out`, falls inside the package when you run from the package folder).
- Use `--prompt-file` / `--neg-file` (UTF-8, up to 64 KiB, trailing newlines dropped) for anything
  private: a command line is readable by every local user. Without a prompt the model's default
  prompt is used.

| option | value | meaning |
|---|---|---|
| `--steps N` | 1 – 1000 | denoise steps |
| `--frames N` | 4k+1; ≤ 1001 one-shot, ≤ 4001 with `--window-frames`, ≤ 65535 with `--stream yes` | frames to render |
| `--width W`, `--height H` | multiples of 16, 16 – 4096 | render size |
| `--guidance G`, `--guidance2 G2` | 0.001 – 50 | classifier-free guidance; `--guidance2` is the low-noise expert (two-expert models) |
| `--seed N` | 0 – 2147483647 | noise seed |
| `--shift S` | 0.001 – 50 | flow shift (default: the per-resolution preset, §1) |
| `--mode M` | `quality` · `balanced` · `fast` · `ultrafast` | §5 |
| `--image FILE` | raw 8-bit RGB | image-to-video first frame (below) |
| `--extend DIR` | a previous I2V `--out` | continue that render: its last frame becomes this render's `--image` (new `--out`, same size) |
| `--png-step N` | 0 – 65535 | write every N-th frame as PNG (0 = none; frames stay in `work/frames.bin`) |
| `--lora FILE`, `--lora-scale s` | safetensors; 0 – 4 | merge a LoRA at load into the (high-noise / only) transformer: W += s · B·A |
| `--lora-check yes` | | report LoRA tensors that match no weight |
| `--det-vae yes` | | deterministic VAE encode / decode (§8) |
| `--gemm-fuse 15` | 0 – 15 | fused GEMM epilogues, bit-identical |

**Image to video.** `--image FILE` is the first frame as raw 8-bit RGB, row-major, no header,
exactly `width × height × 3` bytes at the render size. Resize before: the model card keeps the aspect
within 480 × 832 pixels with sides that are multiples of 16. `--image` is required for a one-shot I2V
render and not allowed with `--stream yes` (use `@image` in the story instead).

**Output.** `DIR/frames/frame_00000.png …` and `DIR/work/` (`frames.bin` u8 [F][H][W][3], `latent.bin`,
per-stage logs `stage_<S>.log` and `time_<S>.txt`, `progress`). Nothing is written inside the package.

---

## 5. Modes

One weight format ships; the modes differ only in the internal compute path.

| mode | what it is | bit-identical to `quality` |
|---|---|---|
| `quality` *(default)* | highest quality, the reference render path | yes |
| `balanced` | near-reference quality, faster | no |
| `fast` | faster, with a small quality trade-off | no |
| `ultrafast` | fastest, with the largest quality trade-off; new in 1.2.0 | no |

The 1.1.0 names changed meaning. `--mode-ladder 1` keeps them (1.1.0 `balanced` = `quality`,
1.1.0 `fast` = `balanced`, 1.1.0 `ultrafast` = `fast`); a 1.1.0 script that passes `--mode` should add
`--mode-ladder 1` or switch to the new names. `--mode low-memory` is not available in this package.

---

## 6. Long video: stream and story

`--stream yes --window-frames 81` renders a long video window by window on a timeline in
`DIR/work/tl`: every window holds the end of the previous one and commits new frames, and device
memory stays at one window's. `--story FILE` drives it with lines of the form `<frame><TAB><text>`:

| line | effect |
|---|---|
| `@def NAME = DESCRIPTION` | a person, object or place; `@NAME` in a scene expands to its description |
| `@set NAME.ATTR = VALUE` | change one attribute (`@unset NAME.ATTR`, `@drop NAME` forgets) |
| `@style = TEXT` | appended to every scene prompt |
| `@image NAME = FILE` | a picture (raw RGB at the render size) becomes visual memory `NAME` |
| `@cut [from] NAME[:s]` | a new shot; `from` = the shot starts at memory `NAME`, otherwise `NAME` is a soft reference for the first `s` of the steps |
| `@keep NAME` | save this frame as visual memory `NAME` |
| scene text | the prompt from this frame on |

- A story with `@gen` anchors is refused: it needs a feature this package does not ship.
- `./inject.sh --out DIR --at FRAME --prompt-file FILE` adds a line to a running stream.
- `--window-adapt yes` makes a window that stops early at a cut cost only what it commits. Each shot
  is decoded with fresh decoder caches, so cuts do not ghost.
- `--branch-from DIR --branch-at FRAME` starts a new render from another render's timeline.
- Without `--stream`, `--window-frames` renders a one-shot text-to-video long video in overlapping
  windows (`--window-overlap`, default 16), and `--prompt2` / `--prompt2-at` and `--prompt3` /
  `--prompt3-at` change the prompt at a frame.

---

## 7. Interruption, preemption, resume, progress

- A one-shot render writes its sampler state to `DIR/work/s4.ckpt` after every step
  (`--checkpoint-every N`; `0` = off, which also disables preemption). If it is interrupted (crash,
  kill, reboot), run the same command again with `--resume yes` and the same `--out`: the run checks
  the render condition against the checkpoint and continues. The result is bit-identical to an
  uninterrupted render.
- To preempt a running render on purpose, create `DIR/work/preempt` (a stream: `DIR/work/tl/preempt`).
  It saves its state at the next step (stream: window) boundary and exits **75** (`VZ_PREEMPTED` /
  `VZ_STREAM_YIELD`); resume as above.
- `DIR/work/progress` always holds one JSON line (schema `vz_progress/1`), replaced atomically at
  every stage boundary and after every denoise step, so a server never has to parse logs. Keys:
  `state` (`running|done|failed|preempted|yielded`), `stage`, `phase`, `step`, `steps`, `expert`,
  `window`, `frames_committed`, `frames_total`, `eta_ms`, `rc`.

---

## 8. Resident mode (`bin/wan_res`)

The WAN package renders to PNG frames; it has no HTTP server. Resident mode is a file-driven daemon for running many renders in one process, as the package's own README.txt documents it.

One process and one CUDA context render request after request: the stages run in it in order, each
stage's GPU memory is released when it ends, and with `WAN_RES_TAPE_MB` set the transformer weights
stay in host RAM after the first load. Results are bit-identical to `./veizik run`.

- Start `bin/wan_res` with `WAN_RES_GO=<file>`. For each request write `<file>.env` (NUL-separated
  `KEY=VALUE` entries — the stage variables the pipeline would set; `-KEY` unsets) and then `<file>`
  containing `1` (render) or `q` (quit), each by rename. `WAN_RES_STAGES` lists the stages (for
  example `2467`; image to video `23467`).
- Every request re-checks the licence (and its model, mode and feature policy) before any stage runs.
  A refused request prints `VZ_RESIDENT_REFUSED` and is skipped; an expired or replaced licence ends
  the daemon (exit 70).
- A request with `WAN_PREEMPT=<file>` is preempted at a step boundary when that file appears
  (`VZ_RESIDENT_PREEMPTED`); post it again with the same `WAN_CKPT` to resume.
- A request cannot change `WAN_PTX`, `VZ_*` or `LD_*` (ignored and logged).

---

## 9. Reproducibility

Same inputs give the same latent bytes on the same GPU architecture: seeded noise, a fixed launch
order and no atomic reductions in the transformer. `FINAL_LATENT_SHA256` (printed at the end of a
run) is the reference; `CONFORMANCE.json` lists the expected hashes for each model, measured on an
RTX 3090. Judge a change on short (1-, 4-, 8-step) latents. The decoded frames are byte-exact with
`--det-vae yes`; without it the VAE may differ by 1 in a few pixels.

```bash
./veizik run wan21_t2v_1_3b --out ~/wan-check --steps 4    # compare FINAL_LATENT_SHA256 with CONFORMANCE.json
```

Every speed figure Veizik states for this package was measured on an RTX 3090 (`sm_86`) only. Other
GPUs run their own kernel sets at speeds not measured.

---

## 10. Integrity seal and provenance mark

- **Integrity.** Before any stage runs, `bin/vzseal` re-hashes every file of the package against
  `SHA256SUMS.vz` and refuses any file the manifest does not list. A modified, added or missing file
  stops the run with exit **4** and a line `VZSEAL MISMATCH <path>` or `VZSEAL FAIL <reason>`. Check by
  hand with `bin/vzseal <package folder>`.
- **Provenance mark.** Every generated frame carries a v1 provenance mark: an in-pixel watermark plus
  XMP `DigitalSourceType=trainedAlgorithmicMedia`. The mark holds no prompt, device, path or account
  data. The provenance stage writes its output to `DIR/provenance/`.

---

## 11. Exit codes

| code | meaning |
|---|---|
| `0` | rendered |
| `2` | usage: bad or unknown option, value out of range, unknown model or mode |
| `3` | an input is missing or unreadable (weights, image, story or schedule file), or a story / encode / decode helper failed |
| `4` | integrity seal failed (`VZSEAL FAIL` / `VZSEAL MISMATCH`) |
| `68` | stream decode of a window failed |
| `69` | a stage reported non-finite values |
| `70` | activation required (no, wrong-device or expired lease: `VZ_ACTIVATION_REQUIRED`), or a stage did not report success |
| `71` | a stage output has the wrong size (1.1.0 used 75 here) |
| `72` | a device kernel the stage asked for did not load |
| `73` | cannot create or write in `--out` |
| `74` | entitlement refused: the lease is valid but its policy does not enable this model, mode or feature, or the policy block is malformed (`VZ_ENTITLEMENT_REFUSED`) |
| `75` | preempted / yielded (`VZ_PREEMPTED` / `VZ_STREAM_YIELD`); continue with `--resume yes` |
| `76` | decoded frames carry no signal |
| `77` | the PNG writer wrote the wrong number of files |
| `78` | package path unresolvable, or the engine refused a compute variant |
| `79` | the engine refused its inputs (usage) |
| `80` | `--init-latent` has the wrong size |
| `83` | persisted cross-attention K/V file short read |
| other | a stage's own non-zero code, passed through |

---

## 12. Not in this package

- `--wcache` (weight cache) and the `--lora-xkv-*` options are disabled; they are refused (exit 2).
- `--lora2` (a LoRA for the low-noise expert), `--i2v-mask-held`, `--i2v-svi` and `--i2v-motion` are
  refused (exit 2).
- `@gen` anchors in a story are refused.
- `--mode low-memory` is not available.

Licence: the Veizik distribution licence ([`../../LICENSE`](../../LICENSE)) and the Veizik Terms of
Service (https://veizik.com/terms). Third-party works: [`../../NOTICE.md`](../../NOTICE.md) and the
package's `THIRD_PARTY_NOTICES.txt`. The Wan weights carry their publisher's Apache-2.0 licence,
including the acceptable-use terms of the model cards. Support: support@veizik.com.
