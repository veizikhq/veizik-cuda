# veizik-cuda

![release](https://img.shields.io/badge/release-flux_1.0.4_sd35_1.0.0_qwen_1.1.4_wan_1.2.92-1f6feb)
![platform](https://img.shields.io/badge/platform-Linux_x86--64_NVIDIA_sm__80--sm__120a-444)
![dependencies](https://img.shields.io/badge/dependencies-NVIDIA_driver_only-2ea043)
![licence](https://img.shields.io/badge/licence-free_for_personal_and_eval-informational)

**Run language, video and image models on your own NVIDIA GPU with one native engine.**
Veizik runs Qwen3.5 / Qwen3.6 language models, Wan2.1 / Wan2.2 video models, and FLUX.1 / Stable Diffusion 3.5 image models on Linux with an NVIDIA GPU. It reads the Hugging Face checkpoint you downloaded yourself. No Python, no framework, no CUDA toolkit, no cloud at inference time: only the NVIDIA driver. Prompts, generated text and generated frames stay on the machine.

### At a glance
- **One native engine, no stack.** No Python, no PyTorch/diffusers, no CUDA toolkit — only the NVIDIA driver. The engine is built from scratch in Veizik's own language and ships as a sealed, checksummed package.
- **Your own weights.** Bring the Hugging Face checkpoint you downloaded; nothing is uploaded and nothing is written back to it. Prompts, generated text and generated frames stay on the machine.
- **Language + video from one toolchain.** Qwen3.5/3.6 (chat, OpenAI-compatible `serve`, and image/video *input* on 35B-A3B) and Wan2.1/2.2 text-to-video and image-to-video — the same `run` / `chat` / `serve` commands for every model.
- **Fits a consumer card.** A 35B-A3B mixture-of-experts language model runs resident in ≈21.7 GiB, and a 14B video model renders 720p on a 24 GB card — weights stream to the GPU instead of loading into system RAM.
- **Built for a render queue.** `serve` is a resident render server: the model loads once, requests reuse it with no reload, an urgent request preempts a running render at a step boundary (checkpoint, serve, resume) and the result is bit-identical to a one-shot run.
- **Deterministic and resumable.** Greedy decode is reproducible; a WAN render resumes bit-identically after an interruption; `--det-vae yes` gives byte-exact frames. Every engine verifies its own files at each start.

## Who this is for
Developers and teams who run open models on their own NVIDIA hardware and want a sealed native engine instead of a framework stack: a one-shot `run`, an interactive `chat`, or a local HTTP server (`serve`) — an OpenAI-compatible API for language models and a render API for video — with the same commands for every model.

## What it looks like
```text
$ veizik run qwen35_2b "The capital of France is" --tokens 32
$ veizik chat qwen35_2b
$ veizik serve qwen35_2b --port 8000          # OpenAI API: POST /v1/chat/completions
```
```text
$ veizik run wan21_t2v_1_3b "A red car driving along a coastal road at sunset." --out $HOME/clip
$ ls $HOME/clip/frames      # frame_00000.png ...
$ veizik serve wan21_t2v_1_3b --port 8000      # render API: POST /v1/videos/generations
```

## Generated on this engine

<p align="center">
  <a href="https://veizik.com/gallery"><img src="https://veizik.com/media/wan_i2v/bird_quality.webp" width="32%" alt="AI-generated image-to-video still of a bird, Wan2.2-I2V-A14B on an RTX 3090."></a>
  <a href="https://veizik.com/gallery"><img src="https://veizik.com/media/wan_i2v/cat_quality.webp" width="32%" alt="AI-generated image-to-video still of a cat, Wan2.2-I2V-A14B on an RTX 3090."></a>
  <a href="https://veizik.com/gallery"><img src="https://veizik.com/media/wan_i2v/astro_quality.webp" width="32%" alt="AI-generated image-to-video still of an astronaut, Wan2.2-I2V-A14B on an RTX 3090."></a>
</p>
<p align="center">
  <a href="https://veizik.com/gallery"><img src="https://veizik.com/media/wan_i2v/guitar_quality.webp" width="32%" alt="AI-generated image-to-video still with a guitar, Wan2.2-I2V-A14B on an RTX 3090."></a>
  <a href="https://veizik.com/gallery"><img src="https://veizik.com/media/wan_i2v/landscape_quality.webp" width="32%" alt="AI-generated image-to-video still of a landscape, Wan2.2-I2V-A14B on an RTX 3090."></a>
</p>

<p align="center"><sub>Image-to-video, generated on the shipped <b>veizik-wan 1.2.92</b> — Wan2.2-I2V-A14B (distilled Lightning), RTX 3090, 832×480 · 81 frames · ~5 s each. Stills shown here; <b><a href="https://veizik.com/gallery">watch the clips at veizik.com/gallery</a></b>. Every frame is AI-generated and carries a v1 provenance mark. Powered by Wan-AI / Alibaba (Wan2.2, Apache-2.0).</sub></p>

**Reproduce it** — bring your own first-frame image, an activated device, and the Wan2.2-I2V-A14B weights:

```bash
veizik run wan22_i2v_a14b "a bird takes off from a branch" \
  --image first_frame.png --out ./clip --mode quality
# 832×480 · 81 frames written to ./clip/frames/ · warm pipeline wall time on an RTX 3090:
# ~226 s quality · ~201 s balanced · ~158 s ultrafast (five runs each)
```

## Supported environment and models
- Linux x86-64, running natively or under WSL2 on Windows with the current NVIDIA Windows driver, with an NVIDIA GPU of compute capability 8.0 or newer and a driver that provides `libcuda.so.1`. No CUDA toolkit and no Python are needed. One GPU runs one model.
- GPU code ships as a separate precompiled set per architecture: `sm_80` (A100), `sm_86` (RTX 3090, RTX A5000, A40), `sm_89` (RTX 4090, L4, L40S), `sm_90a` (H100), `sm_100a` (B200), `sm_120a` (RTX 5090, RTX PRO 6000 Blackwell). A GPU architecture not in this list has no GPU code in these packages.
- Every device is activated once (https://veizik.com/activate). The engines open their GPU code only on an activated device.
- Model weights are not included. You download each checkpoint from its publisher, under the publisher's licence.

**Language — veizik-qwen-cuda 1.1.4** (5 models in one package)

| Model key | Model | Hugging Face checkpoint | Chat | Image and video input | Resident GPU memory, `balanced` |
|---|---|---|---|---|---|
| `qwen35_0p8b` | Qwen3.5-0.8B | `Qwen/Qwen3.5-0.8B` | yes | — | ≈ 2.5 GiB |
| `qwen35_2b` | Qwen3.5-2B | `Qwen/Qwen3.5-2B` | yes | — | ≈ 3.7 GiB |
| `qwen35_4b` | Qwen3.5-4B | `Qwen/Qwen3.5-4B` | yes | — | ≈ 5.7 GiB |
| `qwen35_9b` | Qwen3.5-9B | `Qwen/Qwen3.5-9B` | yes | — | ≈ 8.7 GiB |
| `qwen36_35b_a3b` | Qwen3.6-35B-A3B (mixture of experts, about 3B active per token) | `Qwen/Qwen3.6-35B-A3B` | yes | yes — `--image` / `--video` | ≈ 21.7 GiB (text) |

- All five models are marked **EXPERIMENTAL** in the signed model catalogue.
- Resident memory is measured after load with text input on an RTX 5090 (1.0.0 build); long prompts, images, video and serving need more.
- **Image / video input is Qwen3.6-35B-A3B only** — one PNG or JPEG image, or one folder of 2–256 frames, per run, with a text prompt. Its stage ships GPU code for `sm_86`, `sm_89`, `sm_120a`; on any other GPU the run is refused cleanly with code 50 before any image or video work.
- Validation ran on RTX 3090, A5000, 4090 and 5090; the `sm_80`, `sm_90a` and `sm_100a` GPU code is included but was not run in validation.

**Video — veizik-wan 1.2.92** (4 models in one package, with a resident render server and mid-render preempt)

| Model key | Model | Hugging Face checkpoint | Task | Defaults (size · frames · steps) |
|---|---|---|---|---|
| `wan21_t2v_1_3b` | Wan2.1-T2V-1.3B | `Wan-AI/Wan2.1-T2V-1.3B-Diffusers` | text to video | 832×480 · 49 · 30 |
| `wan21_t2v_14b` | Wan2.1-T2V-14B | `Wan-AI/Wan2.1-T2V-14B-Diffusers` | text to video | 832×480 · 49 · 30 |
| `wan22_t2v_a14b` | Wan2.2-T2V-A14B (two experts) | `Wan-AI/Wan2.2-T2V-A14B-Diffusers` | text to video | 1280×720 · 81 · 40 |
| `wan22_i2v_a14b` | Wan2.2-I2V-A14B (two experts) | `Wan-AI/Wan2.2-I2V-A14B-Diffusers` | image to video | 832×480 · 81 · 40 |

The WAN package carries six kernel sets, one per architecture: `sm_80`, `sm_86`, `sm_89`, `sm_90a`, `sm_100a` and `sm_120a`. Every speed figure Veizik states for this bundle was measured on an RTX 3090 (`sm_86`) only; other GPUs run their own kernel sets at speeds not measured.


**Image — veizik-flux 1.0.4** (8 FLUX.1 [dev] pipelines in one package)

| Model key | Model | Hugging Face checkpoint | Task |
|---|---|---|---|
| `flux1dev` | FLUX.1 [dev] | `black-forest-labs/FLUX.1-dev` | text to image |
| `fluxschnell` | FLUX.1 [schnell] | `black-forest-labs/FLUX.1-schnell` | fast text to image |
| `fluxkrea` | FLUX.1 Krea [dev] | `black-forest-labs/FLUX.1-Krea-dev` | text to image |
| `fluxcanny` | FLUX.1 Canny [dev] | `black-forest-labs/FLUX.1-Canny-dev` | edge-conditioned image to image |
| `fluxdepth` | FLUX.1 Depth [dev] | `black-forest-labs/FLUX.1-Depth-dev` | depth-conditioned image to image |
| `fluxfill` | FLUX.1 Fill [dev] | `black-forest-labs/FLUX.1-Fill-dev` | inpaint / outpaint |
| `fluxkontext` | FLUX.1 Kontext [dev] | `black-forest-labs/FLUX.1-Kontext-dev` | image editing |
| `fluxredux` | FLUX.1 Redux [dev] | `black-forest-labs/FLUX.1-Redux-dev` | image variation |

The FLUX package ships per-architecture GPU code like the others (`sm_80` … `sm_120a`). Text-to-image uses `--steps` / `--seed` / `--mode`; the conditioned pipelines take `--image` (and `--mask` for Fill). Every generated PNG carries a v1 provenance mark (XMP `DigitalSourceType=trainedAlgorithmicMedia`). Weights are the public Black Forest Labs checkpoints you download yourself, under their licence.

## Install and first run
Step 1 installs the `veizik` command (the latest release); it then installs the packages. On macOS the script points you to the Apple disk image instead.

```bash
curl -fsSL https://veizik.com/install.sh | sh   # installs the veizik command only, sha-checked against this repository's SHA256SUMS
export PATH="$HOME/.local/bin:$PATH"
veizik list                           # model engines: installed and available
veizik install qwen36                 # Qwen package (release v1.1.4)
veizik install wan22                  # WAN package (release v1.2.92)
veizik install sd35                   # SD3.5 package (release v1.0.0)
veizik install flux                   # FLUX.1 image package (release v1.0.4)
veizik activate                       # opens veizik.com/activate — approve this machine once
#   no browser (SSH, servers)? create a key under "Browser-free activation" and a password under "CLI password"
#   on your account page, then:  veizik activate --key vzek_… --password-stdin < pwfile
export VZ_WEIGHTS=/data/models        # a folder holding Qwen3.5-0.8B/ and the other checkpoints you downloaded
veizik run qwen35_2b "The capital of France is" --tokens 32
veizik run qwen36_35b_a3b "Explain attention in one paragraph."
veizik chat qwen35_2b                 # interactive REPL (needs an activated device + weights)
veizik serve qwen35_2b --port 8000    # OpenAI API: POST /v1/chat/completions (needs activation)
veizik run wan22_t2v_a14b "A red car driving along a coastal road at sunset." --out $HOME/clip
veizik serve wan22_t2v_a14b --port 8000   # WAN render API: POST /v1/videos/generations (needs activation)
veizik ps                             # resident servers running here
veizik stop 8000                      # stop the server on a port (or: veizik stop all)
veizik uninstall qwen36               # removes an installed package (alias: veizik rm)
```
<details>
<summary><b>Command vocabulary, flags, and per-model notes</b> (click to expand)</summary>

- Every model answers the same commands: `run`, `chat`, `serve`, `ps`, `stop`, `models`, `list`, `install`, `update`, `uninstall` / `rm`, `pull`, `hf`, `remove`, `convert`, `inspect`, `bench`, `cache`, `config`, `completion`, `status`, `activate`, `devices`, `device-id`, `doctor` and `version`; `veizik <command> --help` gives the detail and [`cuda_deploy/CLI_USAGE.md`](cuda_deploy/CLI_USAGE.md) is the full reference. `veizik update` and `veizik convert` exist but are not functional yet.
- Install names are keywords: the Qwen package is `qwen`, `qwen35`, `qwen36` or any of its model keys (`qwen35_0p8b`, `qwen35_2b`, `qwen35_4b`, `qwen35_9b`, `qwen36_35b_a3b`); the WAN package is `wan`, `wan21`, `wan22` or any of its model keys (`wan21_t2v_1_3b`, `wan21_t2v_14b`, `wan22_t2v_a14b`, `wan22_i2v_a14b`). Case does not matter, and `.` or `-` may stand for `_`.
- `veizik install` downloads the package anonymously from this repository's release, refuses it if its sha256 differs from the published release digest, and installs it to `${XDG_STATE_HOME:-~/.local/state}/veizik/engines/<model>/`. It refuses to run on macOS. `veizik run`, `veizik chat` and `veizik serve` find the installed engine themselves.
- `veizik chat` is an interactive REPL; `veizik serve` hosts a local HTTP server on `127.0.0.1` (omit the model to serve every installed one). For Qwen, `serve` is OpenAI-compatible (`POST /v1/chat/completions`, `/v1/completions`, `/v1/models`, health endpoints; `--require-auth --keyfile` requires an API key); for WAN, `serve` is a render API (`POST /v1/videos/generations` with `{"prompt","seed"}` → a folder of PNG frames; `GET /health`, `GET /v1/models`). `run`, `chat` and `serve` generate only after `veizik activate` **and** with the model weights present (`VZ_WEIGHTS`, `--weights DIR` where the command takes it, or the `veizik pull` cache); until the device is activated a request is refused (HTTP 403 / exit 70).
- One flag vocabulary for `run`: `--out`, `--name`, `--resume`, `--resume-from REF` and `--checkpoint-every` work for every model; the rest are forwarded only if the engine accepts them (Qwen: `--seed --steps --mode --temperature --top-p --top-k --tokens --max-tokens --ignore-eos`, plus `--image --video --image-max-pixels --video-fps --video-max-pixels` on Qwen3.6-35B-A3B; WAN: `--steps --frames --width --height --seed --png-step --guidance --guidance2 --shift --mode --det-vae --image --neg-file`), and a flag the engine does not accept is refused with `<flag> does not apply to this model.` `--resume-from REF` resumes that run's folder; See [`cuda_deploy/CLI_USAGE.md`](cuda_deploy/CLI_USAGE.md).
- Download each checkpoint's full Hugging Face snapshot (`config.json`, `tokenizer.json`, `tokenizer_config.json` and every `*.safetensors` file), or fetch weights with `veizik pull <model>` (`veizik hf login` first for a gated model).
- Qwen image and video input (Qwen3.6-35B-A3B only): `veizik run qwen36_35b_a3b "What is in this picture?" --image photo.png` (photo.png: any PNG or JPEG of yours), or `--video ./frames` (a folder of frames) with `--video-fps`.
- WAN: frames land in `<run folder>/frames/`. `veizik serve` answers with the same frames through the HTTP render API; see [`cuda_deploy/wan/README.md`](cuda_deploy/wan/README.md).
- WAN activation: one `veizik activate` approval covers every installed model, WAN included. Without activation every WAN GPU stage stops before any compute and the run exits 70 (`VZ_ACTIVATION_REQUIRED`). WAN needs a 16-channel video-decoder (VAE) layout prepared from your WAN2.1/2.2 checkpoint: `veizik pull wan22` prepares it automatically after fetching the weights (idempotent and crash-safe), and `veizik pull --prep-local DIR` prepares weights already on disk. Standard WAN2.1 (1.3B / 14B) needs no manual step.

</details>

### Checksums (published release digests)
`veizik install` downloads each package and verifies it against its published release digest automatically — there is no separate manual install step. For reference (e.g. to verify a direct download), the published downloads and digests are:
- `veizik-qwen-cuda-1.1.4-linux-x86_64.vzpack` — https://github.com/veizikhq/veizik-cuda/releases/download/v1.1.4/veizik-qwen-cuda-1.1.4-linux-x86_64.vzpack — sha256 `0d925ad92f450e833367834924e4d5d078edab7c546499e214f17b476a930f5e`
- `veizik-shared-core.vzroot` — https://github.com/veizikhq/veizik-cuda/releases/download/v1.1.4/veizik-shared-core.vzroot — sha256 `829f853b945dd6fe403a3c63378fb76ffe5459a65296718d22b0483c4c1db51c`
- `veizik-wan-1.2.92-linux-x86_64.vzpack` — https://github.com/veizikhq/veizik-cuda/releases/download/v1.2.92/veizik-wan-1.2.92-linux-x86_64.vzpack — sha256 `940318320e2e6dc59295f0acebf62c56830ad732df158a6b74859a36bc5c7249`
- `veizik-sd35-1.0.0-linux-x86_64.vzpack` — https://github.com/veizikhq/veizik-cuda/releases/download/v1.0.0/veizik-sd35-1.0.0-linux-x86_64.vzpack — sha256 `cbc273133f6c563e0736984f196496dfb3b00a5953c06a196a6cfb59b7457c6f`
- `veizik-flux-1.0.4-linux-x86_64.vzpack` — https://github.com/veizikhq/veizik-cuda/releases/download/v1.0.4/veizik-flux-1.0.4-linux-x86_64.vzpack — sha256 `66e1e5b770249a4de6af85c0158568b7da298fc002de0c89c06cbf1f595531ab`

What needs the network: installing a package, creating the account, activating the device and renewing its lease. Generation itself does not.

## Measured on this build
- Qwen: the published rows and the rows committed in [`cuda_deploy/bench/`](cuda_deploy/bench/) were measured on 1.0.0 builds of this package (2026-10-21), with text input. They were not re-measured on 1.1.0, and the board marks every row measured on an earlier build. No figure is published for image or video input. Board: https://veizik.com/benchmarks
- Qwen output: greedy decoding is the default and is deterministic. For the committed benchmark prompt the output hash was identical on the RTX 3090, RTX 4090 and RTX 5090 in every measured cell. Sampling (`--temperature`, `--top-p`, `--top-k`, `--seed`) is experimental.
- WAN: the same inputs give the same latent bytes on one GPU architecture. Reference hashes for each model are in the bundle's `CONFORMANCE.json` (measured on an RTX 3090); decoded frames are byte-exact with `--det-vae yes`.

## Full benchmarks and how to reproduce
https://veizik.com/benchmarks — every published row names the GPU, model, mode, operating point, run count and spread. Rows measured on an earlier build are marked. The Qwen rows, the per-run lines they were computed from, and a kit that re-measures them on your GPU through the installed CLI are in [`cuda_deploy/bench/`](cuda_deploy/bench/) — start at [`REPRODUCIBILITY.md`](cuda_deploy/bench/REPRODUCIBILITY.md). The WAN bundle's `REPRO.md` describes how to check a render against `CONFORMANCE.json`.

## Limits, troubleshooting, terms
- Qwen: Qwen3.6-35B-A3B in `quality` mode needs about 26 GB or more and did not complete on a 32 GB card in validation; use `balanced` or `fast`. Image and video input is available for Qwen3.6-35B-A3B only (`veizik run … --image` / `--video`), one image or one video per run. Not in this release: LoRA adapters, audio input, tool calling, embeddings and `logprobs` over HTTP, and a weight converter (`veizik convert` exists but does nothing useful yet; so does `veizik update`).
- WAN: a run that is interrupted continues with `veizik run … --resume` and the same `--out` (or `--resume-from REF`), bit-identical to an uninterrupted render.
- WAN serve: `veizik serve` exposes a render API (`POST /v1/videos/generations` with a prompt and seed → a folder of PNG frames; `/health`, `/v1/models`) on a resident render server (`bin/wan_res`). One process and one GPU context render request after request; results are bit-identical to a one-shot `run`; every request re-checks the licence, and a request can be preempted at a step boundary — the engine checkpoints and yields the GPU, and the preempted request then resumes from its checkpoint and continues to a bit-identical result. It needs `veizik activate` and the weights, like `run`. See [`cuda_deploy/wan/README.md`](cuda_deploy/wan/README.md) §8.
- WAN provenance: every generated frame carries a v1 provenance mark — an in-pixel watermark plus XMP `DigitalSourceType=trainedAlgorithmicMedia`. The mark holds no prompt, device, path or account data.
- Integrity: both engines check their own files at every start. A changed, added or missing file stops the run with exit code 4; reinstall from a verified package. Do not add files inside the installed or unpacked engine folder; write output elsewhere.
- Licensing: a device runs only with a valid lease. Exit 70 means activation is required (`veizik activate`); exit 74 means the lease present was not issued for this package on this device, or does not enable what was asked.
- Not supported: Windows, macOS, GPUs below compute capability 8.0, and splitting one model across several GPUs. The Qwen package also contains an aarch64 `veizik` binary, but the engine is x86-64 only.
- Troubleshooting: `veizik doctor` · `veizik status` · [`cuda_deploy/USAGE_GUIDE.md`](cuda_deploy/USAGE_GUIDE.md) §6 · [`cuda_deploy/wan/README.md`](cuda_deploy/wan/README.md) · https://veizik.com/docs · Issues in this repository · support@veizik.com
- Licence: personal, educational, research and evaluation use at no charge; commercial use needs a separate licence; publishing benchmarks is explicitly allowed. See [LICENSE](LICENSE), [NOTICE.md](NOTICE.md) and the Veizik Terms of Service (https://veizik.com/terms). Model weights stay under their publisher's licence. Veizik is a brand of LinkPick, Seoul.

## Package contents

<details>
<summary>File-by-file manifest of both packages (click to expand)</summary>

**veizik-qwen-cuda-1.1.4-linux-x86_64.vzpack** (v1.1.4, sha256 `0d925ad9…`, 56,694,883 B)
A single-file `.vzpack` (content-addressed, with a signed `.vzindex`) that `veizik install qwen36` verifies against the published digest and materializes to the engine folder `veizik-qwen-cuda-0.1.0-rc1-linux-x86_64-sm86/`: README.txt 1,927 B · install.sh 12,866 B · SHA256SUMS 207,093 B · veizik-x86_64 1,927,696 B · veizik-aarch64 1,242,696 B · PTXSEAL.prov 124 B · PTXSEAL.prov.sig 64 B · the sealed engine folder of the same name: INTERFACE.json 10,540 B · PIPELINE.sh 108 B · SHA256SUMS.vz 132,541 B · models.json 644 B · models.json.sig 64 B · bin/ (8 files, including the image and video runners) · models/ (5 model folders, per-model metadata) · GPU code, 251 files per architecture: `ptx/` (sm_80) · `ptx_sm86/` · `ptx_sm89/` · `ptx_sm90a/` · `ptx_sm100a/` · `ptx_sm120a/` · image and video stage GPU code, 16 files per architecture: `ptx_vis_sm86/` · `ptx_vis_sm89/` · `ptx_vis_sm120a/`. 1,583 files in all. Verify with `sha256sum -c SHA256SUMS` inside the top folder.

**veizik-wan-1.2.92-linux-x86_64.vzpack** (v1.2.92, sha256 `94031832…`, 6,970,958 B)
A single-file `.vzpack` (content-addressed, signed `.vzindex`, shared-core `veizik-shared-core.vzroot`) that `veizik install wan22` verifies against the published digest, checks its signed index and materializes to the engine folder. Same sealed engine and all six per-architecture GPU kernel sets (identical engine; all-architecture support).

**Engine folder** (materialized from the `.vzpack` by `veizik install wan22`)
PTXSEAL.prov 124 B · PTXSEAL.prov.sig 64 B · folder `veizik-wan-1.2.0-linux-x86_64/`: veizik 4,329 B · PIPELINE.sh 48,537 B · README.txt 8,307 B · MODEL.txt 418 B · STAGES.txt 1,239 B · INTERFACE.json 22,444 B · manifest.json 416 B · CONFORMANCE.json 4,099 B · REPRO.md 670 B · PROVENANCE.txt 483 B · THIRD_PARTY_NOTICES.txt 1,070 B · SHA256SUMS.vz 14,702 B · inject.sh 3,390 B · s6_segments.sh 998 B · vz_modes.conf 312 B · bin/ (13 files, incl. the new `veizik-resident` resident host-loop) · bin_seam/ (1 file) · lib/ (15 libraries) · models/ (model folders) · GPU kernel sets: `ptx/` 18 · `ptx_89/` 18 · `ptx_a80/` 19 · `ptx_h90/` 23 · `ptx_b100a/` 21 · `ptx_b120/` 18 files. 177 files in all. The 1.2.92 engine is the Wan 2.2 i2v Lightning LoRA forward-correction (fused int8 mma, `lib/libvzwan.so`) and each of the six GPU kernel sets gains one new LoRA kernel; the opener, `bin/wan_s2` (the 1.2.4 CUDA-13.x non-root fix) and every other kernel are byte-identical to 1.2.8. The folder keeps the version-stable name `veizik-wan-1.2.0-linux-x86_64` so `veizik activate` resolves the same release id across versions. Verify with `bin/vzseal <folder>` (prints `VZSEAL OK 175`).

</details>
