# veizik-cuda

**Run language and video models on your own NVIDIA GPU with one native engine.**
Veizik runs Qwen3.5 / Qwen3.6 language models and Wan2.1 / Wan2.2 video models on Linux with an NVIDIA GPU. It reads the Hugging Face checkpoint you downloaded yourself. No Python, no framework, no CUDA toolkit, no cloud at inference time: only the NVIDIA driver. Prompts, generated text and generated frames stay on the machine.

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

## Supported environment and models
- Linux x86-64, running natively, with an NVIDIA GPU of compute capability 8.0 or newer and a driver that provides `libcuda.so.1`. No CUDA toolkit and no Python are needed. WSL is not a supported runtime for the sealed engines. One GPU runs one model.
- GPU code ships as a separate precompiled set per architecture: `sm_80` (A100), `sm_86` (RTX 3090, RTX A5000, A40), `sm_89` (RTX 4090, L4, L40S), `sm_90a` (H100), `sm_100a` (B200), `sm_120a` (RTX 5090, RTX PRO 6000 Blackwell). A GPU architecture not in this list has no GPU code in these packages.
- Every device is activated once (https://veizik.com/activate). The engines open their GPU code only on an activated device.
- Model weights are not included. You download each checkpoint from its publisher, under the publisher's licence.

**Language — veizik-qwen-cuda 1.1.0** (5 models in one package)

| Model key | Model | Hugging Face checkpoint | Chat | Image and video input | Resident GPU memory, `balanced` |
|---|---|---|---|---|---|
| `qwen35_0p8b` | Qwen3.5-0.8B | `Qwen/Qwen3.5-0.8B` | yes | — | ≈ 2.5 GiB |
| `qwen35_2b` | Qwen3.5-2B | `Qwen/Qwen3.5-2B` | yes | — | ≈ 3.7 GiB |
| `qwen35_4b` | Qwen3.5-4B | `Qwen/Qwen3.5-4B` | yes | — | ≈ 5.7 GiB |
| `qwen35_9b` | Qwen3.5-9B | `Qwen/Qwen3.5-9B` | yes | — | ≈ 8.7 GiB |
| `qwen36_35b_a3b` | Qwen3.6-35B-A3B (mixture of experts, about 3B active per token) | `Qwen/Qwen3.6-35B-A3B` | yes | yes — `--image` / `--video` | ≈ 21.7 GiB (text) |

All five models are marked EXPERIMENTAL in the signed model catalogue. Memory is measured after load with text input on an RTX 5090, on the 1.0.0 build; long prompts, images, video and serving need more. Image and video input is an option of the package's launcher for Qwen3.6-35B-A3B only: one PNG or JPEG image, or one folder of 2–256 PNG or JPEG frames, per run, together with a text prompt. The image and video stage ships GPU code for `sm_86`, `sm_89` and `sm_120a`. On a GPU the image and video stage does not support, the run is refused cleanly with code 50 (`the image stage refused this request (status 50)`) before any image or video work. Validation ran on RTX 3090, RTX A5000, RTX 4090 and RTX 5090; the `sm_80`, `sm_90a` and `sm_100a` GPU code is included but was not run in validation.

**Video — veizik-wan 1.2.0** (4 models in one package, with a resident render server)

| Model key | Model | Hugging Face checkpoint | Task | Defaults (size · frames · steps) |
|---|---|---|---|---|
| `wan21_t2v_1_3b` | Wan2.1-T2V-1.3B | `Wan-AI/Wan2.1-T2V-1.3B-Diffusers` | text to video | 832×480 · 49 · 30 |
| `wan21_t2v_14b` | Wan2.1-T2V-14B | `Wan-AI/Wan2.1-T2V-14B-Diffusers` | text to video | 832×480 · 49 · 30 |
| `wan22_t2v_a14b` | Wan2.2-T2V-A14B (two experts) | `Wan-AI/Wan2.2-T2V-A14B-Diffusers` | text to video | 1280×720 · 81 · 40 |
| `wan22_i2v_a14b` | Wan2.2-I2V-A14B (two experts) | `Wan-AI/Wan2.2-I2V-A14B-Diffusers` | image to video | 832×480 · 81 · 40 |

The WAN package carries six kernel sets, one per architecture: `sm_80`, `sm_86`, `sm_89`, `sm_90a`, `sm_100a` and `sm_120a`. Every speed figure Veizik states for this bundle was measured on an RTX 3090 (`sm_86`) only; other GPUs run their own kernel sets at speeds not measured.

## Install and first run
Step 1 installs the `veizik` command (the latest release); it then installs the packages. On macOS the script points you to the Apple disk image instead.

```bash
curl -fsSL https://veizik.com/install.sh | sh   # installs the veizik command only, sha-checked against this repository's SHA256SUMS
export PATH="$HOME/.local/bin:$PATH"
veizik list                           # model engines: installed and available
veizik install qwen36                 # Qwen package (release v1.1.0)
veizik install wan22                  # WAN package (release v1.2.1)
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
- Every model answers the same commands: `run`, `chat`, `serve`, `ps`, `stop`, `models`, `list`, `install`, `update`, `uninstall` / `rm`, `pull`, `hf`, `remove`, `convert`, `inspect`, `bench`, `cache`, `config`, `completion`, `status`, `activate`, `devices`, `device-id`, `doctor` and `version`; `veizik <command> --help` gives the detail and [`cuda_deploy/CLI_USAGE.md`](cuda_deploy/CLI_USAGE.md) is the full reference. `veizik update` and `veizik convert` exist but are not functional yet.
- Install names are keywords: the Qwen package is `qwen`, `qwen35`, `qwen36` or any of its model keys (`qwen35_0p8b`, `qwen35_2b`, `qwen35_4b`, `qwen35_9b`, `qwen36_35b_a3b`); the WAN package is `wan`, `wan21`, `wan22` or any of its model keys (`wan21_t2v_1_3b`, `wan21_t2v_14b`, `wan22_t2v_a14b`, `wan22_i2v_a14b`). Case does not matter, and `.` or `-` may stand for `_`.
- `veizik install` downloads the package anonymously from this repository's release, refuses it if its sha256 differs from the published release digest, and extracts it to `${XDG_STATE_HOME:-~/.local/state}/veizik/engines/<model>/`. It refuses to run on macOS. `veizik run`, `veizik chat` and `veizik serve` find the installed engine themselves.
- `veizik chat` is an interactive REPL; `veizik serve` hosts a local HTTP server on `127.0.0.1` (omit the model to serve every installed one). For Qwen, `serve` is OpenAI-compatible (`POST /v1/chat/completions`, `/v1/completions`, `/v1/models`, health endpoints; `--require-auth --keyfile` requires an API key); for WAN, `serve` is a render API (`POST /v1/videos/generations` with `{"prompt","seed"}` → a folder of PNG frames; `GET /health`, `GET /v1/models`). `run`, `chat` and `serve` generate only after `veizik activate` **and** with the model weights present (`VZ_WEIGHTS`, `--weights DIR` where the command takes it, or the `veizik pull` cache); until the device is activated a request is refused (HTTP 403 / exit 70).
- One flag vocabulary for `run`: `--out`, `--name`, `--resume`, `--resume-from REF`, `--checkpoint-every` work for every model; the rest are forwarded only if the engine accepts them (Qwen: `--seed --steps --mode --temperature --top-p --top-k --tokens --max-tokens --ignore-eos`, plus `--image --video --image-max-pixels --video-fps --video-max-pixels` on Qwen3.6-35B-A3B; WAN: `--steps --frames --width --height --seed --png-step --guidance --guidance2 --shift --mode --det-vae --image --neg-file`), and a flag the engine does not accept is refused with `<flag> does not apply to this model.` `--resume-from REF` resumes that run's folder; See [`cuda_deploy/CLI_USAGE.md`](cuda_deploy/CLI_USAGE.md).
- Activation ends with one short check generation on `qwen35_0p8b`, so download `Qwen/Qwen3.5-0.8B` first. Download each checkpoint's full Hugging Face snapshot (`config.json`, `tokenizer.json`, `tokenizer_config.json` and every `*.safetensors` file), or fetch weights with `veizik pull <model>` (`veizik hf login` first for a gated model).
- Qwen image and video input (Qwen3.6-35B-A3B only): `veizik run qwen36_35b_a3b "What is in this picture?" --image photo.png` (photo.png: any PNG or JPEG of yours), or `--video ./frames` (a folder of frames) with `--video-fps`.
- WAN: frames land in `<run folder>/frames/`. `veizik serve` answers with the same frames through the HTTP render API; see [`cuda_deploy/wan/README.md`](cuda_deploy/wan/README.md).
- WAN activation: one `veizik activate` approval covers every installed model, WAN included. Without activation every WAN GPU stage stops before any compute and the run exits 70 (`VZ_ACTIVATION_REQUIRED`). The weights folder needs a prepared `vae/` decoder layout (`vae/manifest.txt`) that the package cannot make from the published checkpoint; contact support@veizik.com for it.

### Checksums (published release digests)
`veizik install` downloads each package and verifies it against its published release digest automatically — there is no separate manual install step. For reference (e.g. to verify a direct download), the published downloads and digests are:
- `veizik-qwen-cuda-1.1.0-linux-x86_64.tar` — https://github.com/veizikhq/veizik-cuda/releases/download/v1.1.0/veizik-qwen-cuda-1.1.0-linux-x86_64.tar — sha256 `6217d3c1befd2f9fca3960b9d434efc2ae1b3677db4c57e3e451a91b154e6102`
- `veizik-wan-1.2.1-linux-x86_64.tar` — https://github.com/veizikhq/veizik-cuda/releases/download/v1.2.1/veizik-wan-1.2.1-linux-x86_64.tar — sha256 `3814a7a8aa16552b3074f6bfaec83b9cfe7196df86c723cd9111d7342f2410cd`

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
- WAN serve: `veizik serve` exposes a render API (`POST /v1/videos/generations` with a prompt and seed → a folder of PNG frames; `/health`, `/v1/models`) on a resident render server (`bin/wan_res`). One process and one GPU context render request after request; results are bit-identical to a one-shot `run`; every request re-checks the licence, and a request can be preempted at a step boundary and resumed. It needs `veizik activate` and the weights, like `run`. See [`cuda_deploy/wan/README.md`](cuda_deploy/wan/README.md) §8.
- WAN provenance: every generated frame carries a v1 provenance mark — an in-pixel watermark plus XMP `DigitalSourceType=trainedAlgorithmicMedia`. The mark holds no prompt, device, path or account data.
- Integrity: both engines check their own files at every start. A changed, added or missing file stops the run with exit code 4; reinstall from a verified tarball. Do not add files inside the installed or unpacked engine folder; write output elsewhere.
- Licensing: a device runs only with a valid lease. Exit 70 means activation is required (`veizik activate`); exit 74 means the lease present was not issued for this package on this device, or does not enable what was asked.
- Not supported: Windows, macOS, WSL, GPUs below compute capability 8.0, and splitting one model across several GPUs. The Qwen tarball also contains an aarch64 `veizik` binary, but the engine is x86-64 only.
- Troubleshooting: `veizik doctor` · `veizik status` · [`cuda_deploy/USAGE_GUIDE.md`](cuda_deploy/USAGE_GUIDE.md) §6 · [`cuda_deploy/wan/README.md`](cuda_deploy/wan/README.md) · https://veizik.com/docs · Issues in this repository · support@veizik.com
- Licence: personal, educational, research and evaluation use at no charge; commercial use needs a separate licence; publishing benchmarks is explicitly allowed. See [LICENSE](LICENSE), [NOTICE.md](NOTICE.md) and the Veizik Terms of Service (https://veizik.com/terms). Model weights stay under their publisher's licence. Veizik is a brand of LinkPick, Seoul.

## Package contents

**veizik-qwen-cuda-1.1.0-linux-x86_64.tar** (v1.1.0, sha256 `6217d3c1…`, 57,012,224 B)
Top folder `veizik-qwen-cuda-0.1.0-rc1-linux-x86_64-sm86/`: README.txt 1,927 B · install.sh 3,882 B · SHA256SUMS 207,093 B · veizik-x86_64 1,534,320 B · veizik-aarch64 994,728 B · PTXSEAL.prov 124 B · PTXSEAL.prov.sig 64 B · the sealed engine folder of the same name: INTERFACE.json 10,540 B · PIPELINE.sh 108 B · SHA256SUMS.vz 132,541 B · models.json 644 B · models.json.sig 64 B · bin/ (8 files, including the image and video runners) · models/ (5 model folders, per-model metadata) · GPU code, 251 files per architecture: `ptx/` (sm_80) · `ptx_sm86/` · `ptx_sm89/` · `ptx_sm90a/` · `ptx_sm100a/` · `ptx_sm120a/` · image and video stage GPU code, 16 files per architecture: `ptx_vis_sm86/` · `ptx_vis_sm89/` · `ptx_vis_sm120a/`. 1,583 files in all. Verify with `sha256sum -c SHA256SUMS` inside the top folder.

**veizik-wan-1.2.1-linux-x86_64.tar** (v1.2.1, sha256 `3814a7a8…`, 6,922,240 B)
PTXSEAL.prov 124 B · PTXSEAL.prov.sig 64 B · folder `veizik-wan-1.2.1-linux-x86_64/`: veizik 4,329 B · PIPELINE.sh 45,770 B · README.txt 8,361 B · MODEL.txt 418 B · STAGES.txt 1,239 B · INTERFACE.json 22,507 B · manifest.json 416 B · CONFORMANCE.json 4,181 B · REPRO.md 679 B · PROVENANCE.txt 483 B · THIRD_PARTY_NOTICES.txt 1,070 B · SHA256SUMS.vz 14,114 B · inject.sh 3,390 B · s6_segments.sh 998 B · vz_modes.conf 312 B · bin/ (12 files) · bin_seam/ (1 file) · lib/ (15 libraries) · models/ (model folders: meta.json, default prompt and negative prompt) · GPU kernel sets: `ptx/` 17 · `ptx_89/` 17 · `ptx_a80/` 18 · `ptx_h90/` 22 · `ptx_b100a/` 20 · `ptx_b120/` 17 files. 172 files in all. Verify with `bin/vzseal <folder>` (prints `VZSEAL OK <n>`).
