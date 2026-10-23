# veizik-cuda

**Run language and video models on your own NVIDIA GPU with one native engine.**
Veizik runs Qwen3.5 / Qwen3.6 language models and Wan2.1 / Wan2.2 video models on Linux with an NVIDIA GPU. It reads the Hugging Face checkpoint you downloaded yourself. No Python, no framework, no CUDA toolkit, no cloud at inference time: only the NVIDIA driver. Prompts, generated text and generated frames stay on the machine.

## Who this is for
Developers and teams who run open models on their own NVIDIA hardware and want a sealed native engine instead of a framework stack: a one-shot `run`, an interactive `chat`, or a local HTTP server with OpenAI-compatible request and response shapes for your own tools — and, for video, a scriptable renderer with resume, progress and long-video modes.

## What it looks like
```text
$ veizik run qwen35_2b "The capital of France is" --tokens 32
$ veizik chat qwen35_2b
$ "$VEIZIK_ROOT"/PIPELINE.sh --model qwen36_35b_a3b --image photo.png --prompt "What is in this picture?" --out ./out
$ veizik serve qwen35_2b --weights /data/models/Qwen3.5-2B --port 8000
veizik serve: <model> is serving on http://127.0.0.1:<port>
```
```text
$ ./veizik run wan21_t2v_1_3b --out ./clip --prompt-file prompt.txt
$ ls ./clip/frames      # frame_00000.png ...
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

**Video — veizik-wan 1.2.0** (4 models in one package)

| Model key | Model | Hugging Face checkpoint | Task | Defaults (size · frames · steps) |
|---|---|---|---|---|
| `wan21_t2v_1_3b` | Wan2.1-T2V-1.3B | `Wan-AI/Wan2.1-T2V-1.3B-Diffusers` | text to video | 832×480 · 49 · 30 |
| `wan21_t2v_14b` | Wan2.1-T2V-14B | `Wan-AI/Wan2.1-T2V-14B-Diffusers` | text to video | 832×480 · 49 · 30 |
| `wan22_t2v_a14b` | Wan2.2-T2V-A14B (two experts) | `Wan-AI/Wan2.2-T2V-A14B-Diffusers` | text to video | 1280×720 · 81 · 40 |
| `wan22_i2v_a14b` | Wan2.2-I2V-A14B (two experts) | `Wan-AI/Wan2.2-I2V-A14B-Diffusers` | image to video | 832×480 · 81 · 40 |

The WAN package carries six kernel sets, one per architecture: `sm_80`, `sm_86`, `sm_89`, `sm_90a`, `sm_100a` and `sm_120a`. Every speed figure Veizik states for this bundle was measured on an RTX 3090 (`sm_86`) only; other GPUs run their own kernel sets at speeds not measured.

## Install and first run

**Language (Qwen)**
```bash
curl -LO https://github.com/veizikhq/veizik-cuda/releases/download/v1.1.0/veizik-qwen-cuda-1.1.0-linux-x86_64.tar
echo "d38f30780b873bac616b5b1e7e54a47ee6e8c9dcb5ad18fe47d86a6457852a54  veizik-qwen-cuda-1.1.0-linux-x86_64.tar" | sha256sum -c -
tar xf veizik-qwen-cuda-1.1.0-linux-x86_64.tar
cd veizik-qwen-cuda-0.1.0-rc1-linux-x86_64-sm86   # the folder name is fixed by the release identity; do not rename it
./install.sh                          # checks SHA256SUMS and the engine's own seal, then installs under ~/.local/lib/veizik
export PATH="$HOME/.local/bin:$PATH"
export VZ_WEIGHTS=/data/models        # a folder holding Qwen3.5-0.8B/ and the other checkpoints you downloaded
veizik activate                       # opens veizik.com/activate — approve this machine once
#   no browser (SSH, servers)? create a key under "Browser-free activation" and a password under "CLI password"
#   on your account page, then:  veizik activate --key vzek_… --password-stdin < pwfile
veizik run qwen35_2b "The capital of France is" --tokens 32
veizik chat qwen35_2b                 # interactive; /exit leaves
export VEIZIK_ROOT=$HOME/.local/lib/veizik/veizik-qwen-cuda-0.1.0-rc1-linux-x86_64-sm86   # the installed engine folder
"$VEIZIK_ROOT"/PIPELINE.sh --model qwen36_35b_a3b --image photo.png --prompt "What is in this picture?" --out ./out   # photo.png: any PNG or JPEG of yours
"$VEIZIK_ROOT"/PIPELINE.sh --model qwen36_35b_a3b --video ./frames --video-fps 2 --prompt-file question.txt --out ./out   # ./frames: 2–256 same-size PNG/JPEG frames
veizik serve qwen35_2b --weights /data/models/Qwen3.5-2B --port 8000   # then POST http://127.0.0.1:8000/v1/chat/completions
```
Activation ends with one short check generation on `qwen35_0p8b`, so download `Qwen/Qwen3.5-0.8B` first. Download each checkpoint's full Hugging Face snapshot (`config.json`, `tokenizer.json`, `tokenizer_config.json` and every `*.safetensors` file); `veizik pull` cannot fetch weights for this package.

**Video (WAN)**
```bash
curl -LO https://github.com/veizikhq/veizik-cuda/releases/download/v1.2.0/veizik-wan-1.2.0-linux-x86_64.tar
echo "8a594e6587db6259175936d60e1604a2156d4835e72dcc458dcc685783e8b027  veizik-wan-1.2.0-linux-x86_64.tar" | sha256sum -c -
tar xf veizik-wan-1.2.0-linux-x86_64.tar
cd veizik-wan-1.2.0-linux-x86_64
bin/vzseal "$PWD"                     # integrity check by hand; prints VZSEAL OK <n>
export VZ_WEIGHTS=/data/models/Wan2.1-T2V-1.3B   # transformer/ text_encoder/ tokenizer/ vae/
./veizik run wan21_t2v_1_3b --out ~/wan-out --prompt-file prompt.txt
```
Activating a device for the WAN package: the WAN package carries no activation tool of its own, so contact support@veizik.com to activate a device for it. Activation does not need the model weights; rendering does. The weights folder needs a prepared `vae/` decoder layout (`vae/manifest.txt`) that the package cannot make from the published checkpoint; contact support@veizik.com for it too.
The WAN package runs from the folder you unpacked; it has no installer. Its GPU code opens only on a device activated for this release: without activation every GPU stage stops before any compute and the run exits 70 (`VZ_ACTIVATION_REQUIRED`). The weights folder layout and every option are in [`cuda_deploy/wan/README.md`](cuda_deploy/wan/README.md).

What needs the network: creating the account, activating the device and renewing its lease. Generation itself does not.

## Measured on this build
- Qwen: the published rows and the rows committed in [`cuda_deploy/bench/`](cuda_deploy/bench/) were measured on 1.0.0 builds of this package (2026-10-21), with text input. They were not re-measured on 1.1.0, and the board marks every row measured on an earlier build. No figure is published for image or video input. Board: https://veizik.com/benchmarks
- Qwen output: greedy decoding is the default and is deterministic. For the committed benchmark prompt the output hash was identical on the RTX 3090, RTX 4090 and RTX 5090 in every measured cell. Sampling (`--temperature`, `--top-p`, `--top-k`, `--seed`) is experimental.
- WAN: the same inputs give the same latent bytes on one GPU architecture. Reference hashes for each model are in the bundle's `CONFORMANCE.json` (measured on an RTX 3090); decoded frames are byte-exact with `--det-vae yes`.

## Full benchmarks and how to reproduce
https://veizik.com/benchmarks — every published row names the GPU, model, mode, operating point, run count and spread. Rows measured on an earlier build are marked. The Qwen rows, the per-run lines they were computed from, and a kit that re-measures them on your GPU through the installed CLI are in [`cuda_deploy/bench/`](cuda_deploy/bench/) — start at [`REPRODUCIBILITY.md`](cuda_deploy/bench/REPRODUCIBILITY.md). The WAN bundle's `REPRO.md` describes how to check a render against `CONFORMANCE.json`.

## Limits, troubleshooting, terms
- Qwen server: `veizik serve <model>` hosts one model on `127.0.0.1` only (`--host` accepts only `127.0.0.1` or `localhost`). It answers `POST /v1/chat/completions` (with streaming), `POST /v1/completions` and `GET /v1/models`. Without `--require-auth` it has no authentication; with `--require-auth --keyfile F` every request needs `Authorization: Bearer <key>`. To serve other machines, put a TLS reverse proxy in front of it.
- Qwen server window: each request may use up to 4,096 tokens (prompt plus `max_tokens`); a request that does not fit gets HTTP 400 `context_length_exceeded`. Unsupported request fields are refused with 400, never ignored.
- Qwen: Qwen3.6-35B-A3B in `quality` mode needs about 26 GB or more and did not complete on a 32 GB card in validation; use `balanced` or `fast`. Image and video input is available through the package's launcher for Qwen3.6-35B-A3B only, one image or one video per run; `veizik chat` and `veizik serve` take text only. Not in this release: LoRA adapters, audio input, tool calling, embeddings and `logprobs` over HTTP, a weight converter, and weight downloads with `veizik pull`.
- WAN: a run that is interrupted continues with `--resume yes` and the same `--out`, bit-identical to an uninterrupted render. Long videos render window by window (`--stream yes --window-frames 81`, optionally driven by a `--story` file). A story with `@gen` anchors is refused. `--wcache` is disabled in this bundle.
- WAN: The WAN package renders to PNG frames; it has no HTTP server. `veizik serve` is for the Qwen package only.
- WAN provenance: every generated frame carries a v1 provenance mark — an in-pixel watermark plus XMP `DigitalSourceType=trainedAlgorithmicMedia`. The mark holds no prompt, device, path or account data.
- Integrity: both engines check their own files at every start. A changed, added or missing file stops the run with exit code 4; reinstall from a verified tarball. Do not add files inside the installed or unpacked engine folder; write output elsewhere.
- Licensing: a device runs only with a valid lease. Exit 70 means activation is required (`veizik activate`); exit 74 means the lease present was not issued for this package on this device, or does not enable what was asked.
- Not supported: Windows, macOS, WSL, GPUs below compute capability 8.0, and splitting one model across several GPUs. The Qwen tarball also contains an aarch64 `veizik` binary, but the engine is x86-64 only.
- Troubleshooting: `veizik doctor` · `veizik status` · [`cuda_deploy/USAGE_GUIDE.md`](cuda_deploy/USAGE_GUIDE.md) §6 · [`cuda_deploy/wan/README.md`](cuda_deploy/wan/README.md) · https://veizik.com/docs · Issues in this repository · support@veizik.com
- Licence: personal, educational, research and evaluation use at no charge; commercial use needs a separate licence; publishing benchmarks is explicitly allowed. See [LICENSE](LICENSE), [NOTICE.md](NOTICE.md) and the Veizik Terms of Service (https://veizik.com/terms). Model weights stay under their publisher's licence. Veizik is a brand of LinkPick, Seoul.

## Package contents

**veizik-qwen-cuda-1.1.0-linux-x86_64.tar** (v1.1.0, sha256 `d38f3078…`, 58,573,312 B)
Top folder `veizik-qwen-cuda-0.1.0-rc1-linux-x86_64-sm86/`: README.txt 1,927 B · install.sh 3,882 B · SHA256SUMS 207,093 B · veizik-x86_64 2,519,600 B · veizik-aarch64 1,569,880 B · PTXSEAL.prov 124 B · PTXSEAL.prov.sig 64 B · the sealed engine folder of the same name: INTERFACE.json 10,540 B · PIPELINE.sh 108 B · SHA256SUMS.vz 132,541 B · models.json 644 B · models.json.sig 64 B · bin/ (8 files, including the image and video runners) · models/ (5 model folders, per-model metadata) · GPU code, 251 files per architecture: `ptx/` (sm_80) · `ptx_sm86/` · `ptx_sm89/` · `ptx_sm90a/` · `ptx_sm100a/` · `ptx_sm120a/` · image and video stage GPU code, 16 files per architecture: `ptx_vis_sm86/` · `ptx_vis_sm89/` · `ptx_vis_sm120a/`. 1,583 files in all. Verify with `sha256sum -c SHA256SUMS` inside the top folder.

**veizik-wan-1.2.0-linux-x86_64.tar** (v1.2.0, sha256 `8a594e65…`, 7,112,192 B)
PTXSEAL.prov 124 B · PTXSEAL.prov.sig 64 B · folder `veizik-wan-1.2.0-linux-x86_64/`: veizik 4,329 B · PIPELINE.sh 45,770 B · README.txt 8,361 B · MODEL.txt 418 B · STAGES.txt 1,239 B · INTERFACE.json 22,507 B · manifest.json 416 B · CONFORMANCE.json 4,181 B · REPRO.md 679 B · PROVENANCE.txt 483 B · THIRD_PARTY_NOTICES.txt 1,070 B · SHA256SUMS.vz 14,114 B · inject.sh 3,390 B · s6_segments.sh 998 B · vz_modes.conf 312 B · bin/ (12 files) · bin_seam/ (1 file) · lib/ (15 libraries) · models/ (model folders: meta.json, default prompt and negative prompt) · GPU kernel sets: `ptx/` 17 · `ptx_89/` 17 · `ptx_a80/` 18 · `ptx_h90/` 22 · `ptx_b100a/` 20 · `ptx_b120/` 17 files. 172 files in all. Verify with `bin/vzseal <folder>` (prints `VZSEAL OK <n>`).
