# veizik-wan 1.2.0 — Wan2.1 / Wan2.2 video on NVIDIA GPUs

**Text-to-video and image-to-video with Wan2.1 and Wan2.2 on your own NVIDIA GPU.** Veizik renders
the models through its own native engine — no Python, no framework, no CUDA toolkit, no cloud at render
time. You supply the weights; prompts and frames stay on the machine.

- Package: `veizik-wan-1.2.8-linux-x86_64.vzpack`  ·  SHA-256 `3fbe53c3bedb9158b00b0e1ab9a605af58a9ed5d201cefd2c0bad717ebc3d047`  ·  6,851,149 B
- Models: `wan21_t2v_1_3b`, `wan21_t2v_14b`, `wan22_t2v_a14b`, `wan22_i2v_a14b`
- Hardware: Linux x86-64, NVIDIA GPU with a precompiled kernel set, one per architecture: `sm_80`, `sm_86`, `sm_89`, `sm_90a`, `sm_100a` and `sm_120a`
- Install: `veizik install wan22` — downloads the single-file `.vzpack`, sha-checks it against the release `SHA256SUMS`, verifies its signed index, and materializes the engine folder (full guide: [README](README.md))
- Licence: install + evaluation free; production use licensed. Terms: Veizik Terms of Service (https://veizik.com/terms) and the Veizik distribution licence ([`LICENSE`](../../LICENSE)); third-party works in [`NOTICE.md`](../../NOTICE.md).

Install and run with the `veizik` command (CLI 1.4.3): `veizik install wan22`, `veizik activate` (one approval covers every installed model), then `veizik run wan22_t2v_a14b "<prompt>" --out $HOME/clip`; the full command reference is [`../CLI_USAGE.md`](../CLI_USAGE.md). A package unpacked by hand carries no activation tool of its own; contact support@veizik.com to activate it. Activation does not need the model weights; rendering does. The weights folder needs a prepared `vae/` decoder layout (`vae/manifest.txt`) that the package cannot make from the published checkpoint; contact support@veizik.com for it too.

## In this release

- Four models in one package: Wan2.1-T2V-1.3B, Wan2.1-T2V-14B, Wan2.2-T2V-A14B (two experts) and
  Wan2.2-I2V-A14B (two experts, first frame from `--image`).
- Four render modes: `quality` (default, the reference path), `balanced`, `fast` and `ultrafast`
  (new in 1.2.0). `quality` is bit-identical to the 1.1.0 `balanced` path.
- Long video: stream mode renders window by window on a timeline with device memory held at one
  window's; a story file defines characters, styles, visual memories and cuts; `./inject.sh` adds a
  line to a running stream.
- Resume and preemption: a one-shot render checkpoints every step and continues bit-identically with
  `--resume yes` (`veizik run … --resume`); creating `work/preempt` stops it at the next step boundary with exit 75.
- Progress: `work/progress` holds one JSON line (`vz_progress/1`), replaced atomically after every
  stage and every denoise step.
- Resident server `bin/wan_res`: one process renders request after request, bit-identical to
  `./veizik run`, re-checking the licence on every request; `veizik serve` puts a render API in front of it.
- Provenance mark v1: every generated frame carries an in-pixel watermark plus XMP
  `DigitalSourceType=trainedAlgorithmicMedia`. It holds no prompt, device, path or account data.
- Integrity: `bin/vzseal` re-hashes every file before any stage runs; a changed, added or missing
  file stops the run with exit 4.
- Hardening: the loader that opens the sealed GPU code re-executes itself in a clean environment,
  refuses tracing, keeps its process non-dumpable and checks its own integrity at run time —
  runtime anti-tamper aborts naive binary patches (a determined on-disk patch remains a known
  residual).

## Changed since 1.1.0

- Mode names: the 1.2.0 ladder renames the modes (1.1.0 `balanced` = 1.2.0 `quality`, 1.1.0 `fast`
  = `balanced`, 1.1.0 `ultrafast` = `fast`). `--mode-ladder 1` keeps the 1.1.0 names; 1.1.0 scripts
  that pass `--mode` should add it or switch to the new names.
- A stage output of the wrong size now exits 71 (1.1.0 used 75 here).

## Known issues and limits

- Every speed figure Veizik states for this package was measured on an RTX 3090 (`sm_86`) only;
  other GPUs run their own kernel sets at speeds not measured.
- The transformers and the text encoder must be F32 safetensors as published; a BF16 shard is refused.
- Without `--det-vae yes` the VAE output may differ by 1 in a few pixels between runs; the latents are
  deterministic either way.
- Refused in this package (exit 2): `--wcache`, `--lora-xkv-*`, `--lora2`, `--i2v-mask-held`,
  `--i2v-svi`, `--i2v-motion`, `--mode low-memory`. A story with `@gen` anchors is refused.
- `--out` must be outside the package folder.
- Serve: `veizik serve` exposes a render API on loopback (`POST /v1/videos/generations` with a prompt and seed → a folder of PNG frames; `GET /health`; `GET /v1/models`) on a resident render server (`bin/wan_res`) that renders request after request in one process, bit-identical to a one-shot run, re-checking the licence for every request. It needs `veizik activate` and the weights, like `run`.
- `veizik update` and `veizik convert` exist in the CLI but are not functional yet.
