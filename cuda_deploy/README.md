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
takes one image or one video (a folder of frames) with the text prompt (§4a). This folder is the authoritative support
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
| CLI version (`veizik version`) | `1.2.0` — CLI build `9b000b81` (x86_64); the tarball's aarch64 CLI is build `af92fd50` but the engine is x86-64 only |
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

**Not in this release:** downloading weights with `veizik pull`, a weight converter, LoRA adapters,
image or video input on the four Qwen3.5 models or through `chat` / `serve`, audio input, tool/function calling over HTTP, and usage-ledger / per-tenant quota
enforcement on the CUDA server (an API key is supported: `serve --require-auth`). Each is stated
where it matters in
[`CLI_USAGE.md`](CLI_USAGE.md) and [`USAGE_GUIDE.md`](USAGE_GUIDE.md).

---

## 2. Install

Get the `veizik` command for Linux x86-64 from the latest release of this repository and put it on
your `PATH`.
<!-- TODO(CLI lane): exact install line + sha256 -->

```bash
veizik list                     # the packages you can install
veizik install qwen3-serve      # this package (release v1.1.0); prints the installed path
veizik version                  # veizik 1.2.0 · backend CUDA
export VEIZIK_ROOT=<path printed by install>
veizik doctor                   # root, backend, activation service, integrity of the CLI binary
```

- `veizik install` downloads the package anonymously from this repository's release, refuses it if
  its sha256 differs from the published release digest
  (`d38f30780b873bac616b5b1e7e54a47ee6e8c9dcb5ad18fe47d86a6457852a54`), and extracts it to
  `${XDG_STATE_HOME:-~/.local/state}/veizik/engines/<model>/`. It refuses to run on macOS.
- `veizik uninstall qwen3-serve` (alias `veizik rm`) removes the installed package.
- The installed engine folder is integrity-checked on every start: do not add, remove or edit files
  inside it, and write outputs elsewhere (`--out`, default `~/veizik-out`). If the CLI reports
  `no Veizik NVIDIA engine here`, set `VEIZIK_ROOT` to the path `veizik install` printed.

Uninstall: `veizik deactivate` (see §3), then `veizik uninstall qwen3-serve`.

### Manual install (the package's tarball)

```bash
echo "d38f30780b873bac616b5b1e7e54a47ee6e8c9dcb5ad18fe47d86a6457852a54  veizik-qwen-cuda-1.1.0-linux-x86_64.tar" | sha256sum -c -
# must print: veizik-qwen-cuda-1.1.0-linux-x86_64.tar: OK
tar xf veizik-qwen-cuda-1.1.0-linux-x86_64.tar
cd veizik-qwen-cuda-0.1.0-rc1-linux-x86_64-sm86
./install.sh                  # installs under ~/.local/lib/veizik and puts `veizik` in ~/.local/bin
./install.sh /opt/veizik      # or under a directory of your choice
```

The folder name is fixed by the release identity that activation uses — do not rename it. It
contains GPU code for all six architectures, whatever its name suggests. The installer checks the
`veizik` command against `SHA256SUMS` and the engine against its own integrity seal on a staging copy
**before** anything replaces an existing install. The destination may contain only letters, digits
and `/ . _ - ~ + @ :` and spaces. After a manual install the engine folder is
`~/.local/lib/veizik/veizik-qwen-cuda-0.1.0-rc1-linux-x86_64-sm86` (use it as `VEIZIK_ROOT`); to
remove it, delete `~/.local/bin/veizik` and the folders under `~/.local/lib/veizik`.

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
licence. `veizik pull` reports that it cannot fetch weights for this package, so download them yourself.

```bash
export VZ_WEIGHTS=/data/models        # a folder holding Qwen3.5-0.8B/, Qwen3.5-9B/, …
# or pass --weights /data/models/Qwen3.5-9B to run / serve
```

`run` searches `--weights`, then `VZ_WEIGHTS`, then `VEIZIK_CACHE`, then the Hugging Face cache;
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
- `veizik status` shows this device's lease and expiry. This build has no `device-id` command;
  `veizik devices` lists the devices on your licence, and `veizik deactivate [--forget]` releases
  this one.
- Always go through `veizik activate`: do not create or edit the device-key and lease files yourself,
  and do **not** copy an activated install or its key files to another machine — the lease is bound
  to this device and will not verify elsewhere. Anyone who copies the device key can use your
  activation; keep it private.
- Headless enrolment with an organisation token (`activate --token`) is **not available in this
  release**; the binary recognises the flag only to refuse it.

| exit code | meaning |
|---|---|
| `70` | activation required — no device key, lease, or the lease expired; run `veizik activate` |
| `74` | entitlement refused — a lease is present but was not issued for this package on this device |

---

## 4. Quick start

```bash
export VEIZIK_ROOT=<path printed by install>   # once per shell (§2)

# one-shot generation (greedy by default); the output is written to gen.txt in ~/veizik-out
veizik run qwen35_2b "The capital of France is" --tokens 32

# a larger model, a named mode, a prompt from a file, a chosen output folder
veizik run qwen35_9b --prompt-file question.txt --mode balanced --tokens 256 --out ./out

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
```

### 4a. Image and video input (Qwen3.6-35B-A3B only)

```bash
# the package's launcher (INTERFACE.json entry PIPELINE.sh) in the installed engine folder
export VEIZIK_ROOT=<path printed by install>

# one image (PNG or JPEG) with a text prompt; photo.png stands for your own file
"$VEIZIK_ROOT"/PIPELINE.sh --model qwen36_35b_a3b --image photo.png --prompt "What is in this picture?" --out ./out

# one video: a folder of 2–256 PNG or JPEG frames, all the same size, in file-name order
"$VEIZIK_ROOT"/PIPELINE.sh --model qwen36_35b_a3b --video ./frames --video-fps 2 --prompt-file question.txt --out ./out
```

Each run takes exactly one image or one video, never both, and always with `--prompt` or
`--prompt-file`. The chat template is applied and the answer ends at the end-of-turn token. Details,
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
