# veizik-cuda — Deployment & Support

This folder holds the support documentation for both NVIDIA / Linux packages in this repository:

| package | release | guide | release notes |
|---|---|---|---|
| Qwen3.5 / Qwen3.6 language models — `veizik-qwen-cuda-1.1.0-linux-x86_64.tar` | `v1.1.0` | this file, [`CLI_USAGE.md`](CLI_USAGE.md), [`USAGE_GUIDE.md`](USAGE_GUIDE.md), [`bench/REPRODUCIBILITY.md`](bench/REPRODUCIBILITY.md) | [`RELEASE_NOTES.md`](RELEASE_NOTES.md) |
| Wan2.1 / Wan2.2 video models — `veizik-wan-1.2.0-linux-x86_64.tar` | `v1.2.0` | [`wan/README.md`](wan/README.md) | [`wan/RELEASE_NOTES.md`](wan/RELEASE_NOTES.md) |

The rest of this file covers the Qwen package.

## veizik-cuda 1.1.0 (Qwen3.5 / Qwen3.6)

Veizik runs the Qwen3.5 (0.8B, 2B, 4B, 9B) and Qwen3.6-35B-A3B language models **on your own NVIDIA
GPU** through its own native engine: per-architecture native CUDA code, no Python runtime,
no CUDA toolkit, no cloud at inference time. `veizik serve` provides a local OpenAI-compatible HTTP
server (chat completions, text completions, streaming). On Qwen3.6-35B-A3B, the package's launcher also
takes one image or one video (a folder of frames) with the text prompt (`veizik run … --image` / `--video`, §4a). This folder is the authoritative support
documentation for the shipped CUDA Qwen package — install, activation, every CLI command, serving
over HTTP, and a reproducible benchmark set.

> **Scope.** This covers the CUDA/Linux Qwen package. The WAN video package has its own guide in
> [`wan/`](wan/). The Apple-Silicon (`veizik-metal`) deployment is a separate package with its own
> documentation.

---

## 1. What ships

| Item | Value |
|---|---|
| Product | `veizik-cuda 1.1.0 (Qwen3.5 / Qwen3.6)` |
| Package | `veizik-qwen-cuda-1.1.0-linux-x86_64.tar` (58,573,312 B) |
| Package SHA-256 | `d38f30780b873bac616b5b1e7e54a47ee6e8c9dcb5ad18fe47d86a6457852a54` (short form `d38f3078`) |
| Supersedes | `veizik-cuda 1.0.0`. 1.1.0 adds image and video input on Qwen3.6-35B-A3B; the five text models are unchanged |
| CLI version (`veizik version`) | `1.4.3` — the same CLI serves the Qwen and the WAN package; the engine is x86-64 only |
| Backend | `CUDA` (native kernels, one set per GPU architecture) |
| Signing | engine files integrity-sealed and checked at every start; the release catalogue is signed with Veizik's production code-signing key and can be verified with the bundled public key |
| GPU architectures | `sm_80` / `sm_86` / `sm_89` / `sm_90a` / `sm_100a` / `sm_120a` — GPU code ships as per-architecture cubin (SASS); the loader does no JIT. The image and video stage ships GPU code for `sm_86`, `sm_89` and `sm_120a` |
| Model weights | **not included** — you download the public checkpoints (§2, "Model weights") |

Shipped models (pass the **model key** to the CLI):

| model key | model | Hugging Face repository | notes |
|---|---|---|---|
| `qwen35_0p8b` | Qwen3.5-0.8B | `Qwen/Qwen3.5-0.8B` | also used by the activation check |
| `qwen35_2b` | Qwen3.5-2B | `Qwen/Qwen3.5-2B` | |
| `qwen35_4b` | Qwen3.5-4B | `Qwen/Qwen3.5-4B` | |
| `qwen35_9b` | Qwen3.5-9B | `Qwen/Qwen3.5-9B` | |
| `qwen36_35b_a3b` | Qwen3.6-35B-A3B | `Qwen/Qwen3.6-35B-A3B` | mixture of experts, 35B total / about 3B active per token; image and video input through the package's launcher (§4a) |

**Weights are yours.** The package contains the engine, not the models. You point Veizik at a
checkpoint you already have the right to use; several upstream checkpoints are released under their
own terms and Veizik does not change them. Nothing is uploaded.

**Conversation.** Chat works two ways for all five models. `veizik chat <model>` is an interactive
prompt in your terminal: type a message, read the model's text reply, repeat (each message is answered
on its own). `veizik serve <model>` answers `POST /v1/chat/completions` (with streaming) for programs
and any OpenAI-compatible client, next to `POST /v1/completions` and `GET /v1/models`.

**Not in this release:** a weight converter (`veizik convert` exists but does nothing useful yet, and neither does
`veizik update`), LoRA adapters, image or video input on the four Qwen3.5 models or through `chat` / `serve`, audio input, tool/function calling over HTTP, and usage-ledger / per-tenant quota
enforcement on the CUDA server (an API key is supported: `serve --require-auth`). Each is stated
where it matters in
[`CLI_USAGE.md`](CLI_USAGE.md) and [`USAGE_GUIDE.md`](USAGE_GUIDE.md).

---

## 2. Install

```bash
curl -fsSL https://veizik.com/install.sh | sh   # installs the veizik command only, sha-checked against this repository's SHA256SUMS
export PATH="$HOME/.local/bin:$PATH"
veizik list                     # model engines: installed and available
veizik install qwen36           # this package (release v1.1.3)
veizik version                  # the CLI version and backend
veizik doctor                   # root, backend, activation service, integrity of the CLI binary
```

- The install script installs only the `veizik` command (the latest release), sha-checked against this
  repository's `SHA256SUMS`; on macOS it points you to the Apple disk image instead.
- Install names are keywords: the Qwen package is `qwen`, `qwen35`, `qwen36` or any of its model keys (`qwen35_0p8b`, `qwen35_2b`, `qwen35_4b`, `qwen35_9b`, `qwen36_35b_a3b`); the WAN package is `wan`, `wan21`, `wan22` or any of its model keys (`wan21_t2v_1_3b`, `wan21_t2v_14b`, `wan22_t2v_a14b`, `wan22_i2v_a14b`). Case does not matter, and `.` or `-` may stand for `_`.
- `veizik install` downloads the package anonymously from this repository's release, refuses it if
  its sha256 differs from the published release digest, and installs it to
  `${XDG_STATE_HOME:-~/.local/state}/veizik/engines/<model>/`. It refuses to run on macOS. `veizik run`,
  `chat` and `serve` find the installed engine themselves.
- `veizik uninstall qwen36` (alias `veizik rm`) removes the installed package. `veizik update` exists
  but is not functional yet; to get a newer package, run `veizik install` again.
- The installed engine folder is integrity-checked on every start: do not add, remove or edit files
  inside it, and write outputs elsewhere (`--out`, default `~/veizik-out`). If the CLI reports
  `no Veizik NVIDIA engine here`, set `VEIZIK_ROOT` to the engine folder `veizik install` printed.

Uninstall: `veizik uninstall qwen36`. To free this device's slot on your licence, use `veizik devices disable <tag>` (§3).

### Installing the package

The Qwen package ships as a single content-addressed `.vzpack` file. `veizik install qwen`
downloads it from this repository's release, verifies it against the published `SHA256SUMS` digest
and its signed `.vzindex`, and materialises the engine folder under
`${XDG_STATE_HOME:-~/.local/state}/veizik/engines/<model>/`. There is no separate manual download or
unpack step. The folder name is fixed by the release identity that activation uses — do not rename
it, and it contains GPU code for all six architectures whatever its name suggests. If the CLI reports
`no Veizik NVIDIA engine here`, set `VEIZIK_ROOT` to the engine folder `veizik install` printed.

### System requirements

- **OS:** Linux x86-64, running natively. **WSL is not a supported runtime** for the sealed engine.
- **GPU:** NVIDIA, compute capability 8.0 or newer. One GPU runs one model; splitting a model across
  GPUs is not supported. A GPU architecture not in the table has no GPU code in this package.

  | architecture | example GPUs | run in validation |
  |---|---|---|
  | `sm_80` | A100 | included; not run |
  | `sm_86` | RTX 3090, RTX A5000, A40 | RTX 3090, RTX A5000 |
  | `sm_89` | RTX 4090, L4, L40S | RTX 4090 |
  | `sm_90a` | H100 | included; not run |
  | `sm_100a` | B200 | included; not run |
  | `sm_120a` | RTX 5090, RTX PRO 6000 Blackwell | RTX 5090 |

- **Driver:** a driver that provides `libcuda.so.1` and supports your card. Validation used driver
  595.91.07; no minimum version is stated for this release. No CUDA toolkit and no Python are needed.
- **GPU memory** (resident after load, `balanced`, measured; more is needed for long prompts and
  for serving): Qwen3.5-0.8B ≈ 2.5 GiB, 2B ≈ 3.7 GiB, 4B ≈ 5.7 GiB, 9B ≈ 8.7 GiB,
  Qwen3.6-35B-A3B ≈ 21.7 GiB. `quality` adds roughly 0.15 – 1.4 GiB on the dense models; on
  35B-A3B it needs about 26 GB or more and did not complete on a 32 GB card in validation. Serving
  Qwen3.6-35B-A3B used 27.1 GB of a 32 GB card.
- **Host tools** the installer, launcher and CLI call (present on ordinary Linux installs): `bash`,
  `curl`, `perl`, `xxd`, `od`, `base64`, `sed`, `awk`, `grep`, `timeout`, `mktemp`, `mkfifo`, `tee`,
  `sha256sum`, and `nvidia-smi` (used to read your GPU architecture).
- **Network:** needed for activation and lease renewal. Generation runs on your GPU.
- **Disk:** about 55 MB for the package; the checkpoints you supply are far larger (the 35B model is
  about 70 GB).

### Model weights (before you activate)

Download the Hugging Face snapshot of each model you want (`config.json`, `tokenizer.json`,
`tokenizer_config.json` and every `*.safetensors` file) from its publisher, under the publisher's
licence, or fetch them with `veizik pull <model>[@<revision>]` (run `veizik hf login` first for a gated model).

```bash
export VZ_WEIGHTS=/data/models        # a folder holding Qwen3.5-0.8B/, Qwen3.5-9B/, …
# or pass --weights /data/models/Qwen3.5-9B to serve
```

`run` searches `VZ_WEIGHTS`, then `VEIZIK_CACHE` (the `veizik pull` cache), then the Hugging Face cache;
`serve` needs the checkpoint folder itself (see [`CLI_USAGE.md`](CLI_USAGE.md)). A folder counts only if
it is complete; if nothing matches, the run stops with exit code **3** and lists where it looked.

---

## 3. Activate (once per device)

Activation binds the install to **this machine**. It is per device, not per model: one activation
covers all five models. The device key is generated on this machine, stored with mode `0600` under
`${XDG_STATE_HOME:-$HOME/.local/state}/veizik/cuda/device/`, and never leaves it.

**Get the `Qwen3.5-0.8B` checkpoint first**, whichever model you actually want. Activation ends with
one short check generation that always uses `qwen35_0p8b`; without its weights, activation installs
the lease, reports that the device is **not confirmed** (exit 6), and asks you to run it again once
the weights are present. `veizik activate` has no `--weights`; use `VZ_WEIGHTS` or the Hugging Face
cache.

```bash
VZ_WEIGHTS=/data/models veizik activate         # prints an address and a code; approve it in any browser
veizik status                                   # activation, expiry, key files present
```

Without a browser (SSH, servers, containers): on your account page at https://veizik.com create a
key under "Browser-free activation" and a password under "CLI password", then

```bash
printf '%s' "$CLI_PASSWORD" | veizik activate --key vzek_… --password-stdin
```

- Activation is **per device**. Installing a later release on an approved machine renews silently
  with no browser; `veizik activate --refresh` renews the lease only. `run` and `serve` also renew a
  lease that is within 3 days of expiring.
- `veizik status` shows this device's lease and expiry. `veizik device-id` prints this machine's
  device id (it matches the website list), `veizik devices` lists the devices on your licence, and
  `veizik devices disable <tag>` / `enable <tag>` switches one.
- One approval covers all installed models; `veizik activate <model>` narrows it to one engine.
- Always go through `veizik activate`: do not create or edit the device-key and lease files yourself,
  and do **not** copy an activated install or its key files to another machine — the lease is bound
  to this device and will not verify elsewhere. Anyone who copies the device key can use your
  activation; keep it private.
- Headless enrolment with an organisation token (`activate --token`) is **not available in the shipped
  build**; the binary recognises the flag only to refuse it.

| exit code | meaning |
|---|---|
| `70` | activation required — no device key, lease, or the lease expired; run `veizik activate` |
| `74` | entitlement refused — a lease is present but was not issued for this package on this device |

---

## 4. Quick start

```bash
# one-shot generation (greedy by default); the output is written to gen.txt in ~/veizik-out
veizik run qwen35_2b "The capital of France is" --tokens 32
veizik run qwen36_35b_a3b "Explain attention in one paragraph."

# a larger model, a named mode, a prompt from a file, a chosen output folder (an absolute path)
veizik run qwen35_9b "$(cat question.txt)" --mode balanced --tokens 256 --out $HOME/out

# local OpenAI-compatible HTTP server (loopback only): chat + text completions, streaming supported
veizik serve qwen35_2b --weights /data/models/Qwen3.5-2B --port 8000
curl -s http://127.0.0.1:8000/v1/chat/completions -H 'content-type: application/json' \
     -d '{"model":"qwen35_2b","messages":[{"role":"user","content":"Hello"}],"max_tokens":32}'

# the same server requiring an API key (HTTP 401 without it); keep the key in a file, not on the command line
( umask 077; head -c 24 /dev/urandom | od -An -tx1 | tr -d ' \n' > ~/.veizik-serve.key )
veizik serve qwen35_2b --weights /data/models/Qwen3.5-2B --require-auth --keyfile ~/.veizik-serve.key

# measure this machine
veizik bench qwen35_9b

# interactive chat in the terminal (type a message, read the reply; /exit leaves)
veizik chat qwen35_2b

# resident servers
veizik ps
veizik stop 8000                  # or: veizik stop all
```

`run`, `chat` and `serve` generate only on an activated device and with the model weights present.

### 4a. Image and video input (Qwen3.6-35B-A3B only)

```bash
# one image (PNG or JPEG) with a text prompt; photo.png stands for your own file
veizik run qwen36_35b_a3b "What is in this picture?" --image photo.png

# one video: a folder of 2–256 PNG or JPEG frames, all the same size, in file-name order
veizik run qwen36_35b_a3b "$(cat question.txt)" --video ./frames --video-fps 2
```

Flags: `--image FILE`, `--video DIR`, `--image-max-pixels N`, `--video-max-pixels N`, `--video-fps X`
(only on `qwen36_35b_a3b`; the other models refuse them with `<flag> does not apply to this model.`).

Each run takes exactly one image or one video, never both, and always with a text prompt. The chat template is applied and the answer ends at the end-of-turn token. Details,
limits and exit codes: [`USAGE_GUIDE.md`](USAGE_GUIDE.md) §1a.

`veizik run` writes its output to `gen.txt` in `--out`; for text use `veizik chat` or `veizik serve`. The complete
command reference — every verb, every flag, with examples — is in **[`CLI_USAGE.md`](CLI_USAGE.md)**.

---

## 5. Benchmarks & reproducibility

Veizik publishes its own measured figures only. The decode board for this package (tokens/s of
`veizik run`, `balanced`, 128 generated tokens, median of 2 runs) is:

| model | RTX 3090 | RTX 4090 | RTX 5090 |
|---|---|---|---|
| Qwen3.5-0.8B | 940 | 1318 | 1529 |
| Qwen3.5-2B | 583 | 887 | 1138 |
| Qwen3.5-4B | 369 | 532 | 772 |
| Qwen3.5-9B | 190 | 347 | 499 |
| Qwen3.6-35B-A3B | — | — | 450 (`fast`: 545) |

These rows are **previous-version rows**: they were measured on 1.0.0 builds of this package
(2026-10-21), with text input, and were not re-measured on 1.1.0. No figure is published for image or
video input. Each figure names its GPU, mode, operating point and run count; none
is projected. `quality` mode, per-run values, spread, resident memory and 1,024-token runs are in the
data files.

- Measured result data (committed): [`bench/results/`](bench/results/) — `*_rows.json` per GPU (every
  row: model, arch, gpu, power, axis, value, unit, measured_at, prov, plus per-run values and
  spread) and the neutral per-run measurement lines `*_bench.txt`.
- Reproduction kit (committed): [`bench/repro_kit/`](bench/repro_kit/) — the pinned prompt, its SHA
  manifest, and the grid and extraction scripts. It drives Veizik only through the installed CLI.
- How to reproduce, line by line: **[`bench/REPRODUCIBILITY.md`](bench/REPRODUCIBILITY.md)**.

The board reports Veizik's own numbers only; there is no comparison with other products. Server
throughput over HTTP is not published for this release.

---

## 6. Pointers

| Need | Where |
|---|---|
| Every CLI command and flag | [`CLI_USAGE.md`](CLI_USAGE.md) |
| Run modes, serving over HTTP, long context, sampling, performance, troubleshooting | [`USAGE_GUIDE.md`](USAGE_GUIDE.md) |
| Reproduce the benchmark board | [`bench/REPRODUCIBILITY.md`](bench/REPRODUCIBILITY.md) |
| This release's contents and checksums | [`RELEASE_NOTES.md`](RELEASE_NOTES.md) |
| What `doctor` / `status` assert | `veizik doctor` (CLI binary, install root, activation service), `veizik status` (lease) |
| Licence terms | Install and evaluation are free; production use is licensed. The terms are the Veizik Terms of Service, section "License & entitlement" (https://veizik.com/terms), together with the Veizik distribution licence ([`LICENSE`](../LICENSE) at the root of this repository) and the third-party notices ([`NOTICE.md`](../NOTICE.md)). The tarball itself does not carry a licence file. Model weights stay under their publisher's licence |
| The WAN video package | [`wan/README.md`](wan/README.md) |
| Support | support@veizik.com |
