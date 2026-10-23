# veizik CLI — Complete Command Reference (CUDA / Linux, veizik-cuda 1.1.0, CLI 1.2.0)

Every command the shipped `veizik` binary of this package accepts, its flags, exit codes and a worked
example. Flags and behavior below are taken from the source of the shipped CLI build (`9b000b81`) and
cross-checked against the text the binary itself prints; a flag appears here only if the binary
accepts it. Where a command is present but has a narrower role for this package (for example it works
on a checkpoint you supply, or on the CLI's own local files), the entry says so. Exit codes are listed
for the commands where they matter to a script; for the rest the entry describes what the command
does and prints.

The installer puts one command on your `PATH`: `veizik`. No `vz` alias is installed by this package;
add `alias vz=veizik` yourself if you want the short form.

Built-in help: `veizik --help` (also `-h`, `help`) prints the command summary and exits 0; `veizik`
with no arguments prints it and exits 2. `veizik version` prints the CLI version and backend;
`veizik doctor` checks the installation. A command given missing or unknown arguments prints its own
usage and exits 2. Unknown or mistyped options are errors, never ignored.

```
veizik <command> [arguments]
```

## What works on this package

| command | on this package |
|---|---|
| `run` | works — one-shot generation |
| `serve` | works — starts the engine's own OpenAI-compatible server on loopback: `POST /v1/chat/completions`, `POST /v1/completions`, `GET /v1/models`, streaming; optionally requires an API key (`--require-auth`). **This is the supported way to hold a conversation** |
| `chat` | works — an interactive terminal session: type a message, read the model's text reply, repeat. Available for all five models (the catalogue declares chat for each) |
| `ps`, `stop` | do not manage the CUDA server (it runs in your terminal; stop it with Ctrl-C) |
| `models` | works — lists the five model keys with a per-model status label; the `ON DISK` label is not a readiness check |
| `pull` | present — the CLI's model downloader; for this package it reports that it cannot fetch weights, because the weights are yours to download |
| `hf`, `remove`, `cache` | work on the download cache and token, which this package does not use |
| `convert` | present — a checkpoint checker; this release ships no converter, so it checks and reports and never writes a converted file |
| `inspect` | works — shows a model's catalogue status and whether it can run here; the weights are external, so it reports them as missing |
| `bench` | works — three end-to-end runs, median |
| `config`, `completion` | work |
| `status`, `activate`, `deactivate`, `devices`, `doctor`, `version` | work |
| `device-id` | there is no such command — use `veizik devices` (see "Device, activation, health") |
| `keys`, `usage`, `audit`, `quota`, `gateway` | real standalone local CLI tools; they run normally but are not integrated with the CUDA server — see "Server front-ends and ledgers" |
| `cluster`, `service` | present; see "Server front-ends and ledgers" for what applies to the CUDA server |

## Exit codes (shared across verbs)

| code | meaning |
|---|---|
| `0` | success |
| `1` | `run`/`serve`: the engine failed, or finished without confirming the configuration it ran in (the result is not what you asked for); `status`: the lease is in its renewal grace period |
| `2` | usage error: no args, unknown command, unknown or invalid option, missing or blank argument, out-of-range value, unknown model or mode; for `run`/`serve` also: the engine refused the model configuration, or the GPU generation could not be read (set `Q35_SEAL_ARCH`); image or video input that cannot be used (wrong model, more than one image or video, `--image` with `--video`, no text prompt, an unsupported or damaged file, frames of different sizes or fewer than 2 / more than 256, over the size or aspect-ratio budget, or a GPU the image or video stage does not support) |
| `3` | an input is missing or unreadable: model weights, tokenizer, prompt file, the image file, the video frames folder, or the output folder cannot be created |
| `4` | model not found, or not usable for the command; `status`: not activated or expired; `run`/`serve`: the engine could not start because its integrity check failed (a file was changed, added or removed — reinstall) or its GPU modules did not open |
| `5` | the CLI binary failed its own integrity check; `activate --refresh` could not renew |
| `6` | no engine found at the install root, cannot write, the activation service refused, or activation was not confirmed |
| `70` | activation required — no device key, no lease, or the lease expired; run `veizik activate` |
| `74` | entitlement refused — a lease is present but was not issued for this package on this device |
| `130` | interrupted (Ctrl-C) during `run` or during the activation approval wait |

Once the engine has started, its own exit code is passed through, so `4` can mean "the CLI could not
find the model" or "the engine could not start"; the message printed before it says which.

---

## Use a model

### `run` — generate once and exit

```
veizik run <model> "<prompt>" [options]
veizik run <model> --prompt TEXT | --prompt-file FILE [options]
veizik run qwen36_35b_a3b --image FILE | --video DIR (--prompt TEXT | --prompt-file FILE) [options]
```

- `<model>` — one of the five model keys: `qwen35_0p8b`, `qwen35_2b`, `qwen35_4b`, `qwen35_9b`,
  `qwen36_35b_a3b`. Exact and case-sensitive; display names such as `Qwen3.5-9B` are not accepted.
- The prompt is a quoted second argument, or `--prompt TEXT`, or `--prompt-file FILE` — give it one
  way only. Command-line text is visible in the process list; use `--prompt-file` for long or
  private prompts.
- Options are written `--name value` or `--name=value` and may appear before, between or after the
  positional arguments. An option given twice, or one this package does not define, stops the run
  with exit 2 and nothing is executed. `--model`, `--ignore-eos` and `--lora` are not options of this
  package.
- The prompt is used **as written**: no chat template is applied. For an instruct-style answer, wrap
  the text in the model's chat format yourself (example below).

| option | value | default | meaning |
|---|---|---|---|
| `--mode M` | `quality` · `balanced` · `fast` · `ultrafast` · `low-memory` | `balanced` | quality / memory / speed preset (see [`USAGE_GUIDE.md`](USAGE_GUIDE.md) §5) |
| `--prompt TEXT` | text | — | the prompt; exclusive with `--prompt-file` and with a positional prompt |
| `--prompt-file FILE` | UTF-8 file | — | prompt from a file; must exist and be non-empty (exit 3 otherwise) |
| `--ids-file FILE` | file of whitespace-separated token ids | — | run from token ids instead of text; exclusive with the prompt options |
| `--tokens N` | 1 – 4096 | `128` | number of tokens to generate |
| `--steps N` | 1 – 4096 | — | same as `--tokens` |
| `--weights DIR` | folder | search | folder of the Hugging Face checkpoint of the selected model |
| `--out DIR` | folder | `$VEIZIK_OUT`, else `~/veizik-out` | output folder, created if missing; must be **outside** the installed engine folder |
| `--temperature X` | 0 – 2 | `0` (greedy) | sampling temperature — **experimental** |
| `--top-p X` | 0 – 1 | — | nucleus threshold — **experimental** |
| `--top-k N` | 0 – 1000 | — | top-k — **experimental** |
| `--seed N` | 0 – 2147483647 | — | sampling seed — **experimental** |
| `--image FILE` | PNG or JPEG | — | `qwen36_35b_a3b` only: an image the model looks at; exactly one per run; needs `--prompt` or `--prompt-file`; applies the chat template (the answer ends at the end-of-turn token). `--image-file` is the same option |
| `--image-max-pixels N` | 65536 – 16777216 | `1048576` | upper bound on the image's pixel count after resizing; a larger image is scaled down to fit. More pixels keep more detail and use more memory and time. Needs `--image` |
| `--video DIR` | folder of PNG or JPEG frames | — | `qwen36_35b_a3b` only: 2 to 256 frames, all the same size, in file-name order (= time order); exactly one video per run; needs `--prompt` or `--prompt-file`; not with `--image`; applies the chat template (the answer ends at the end-of-turn token) |
| `--video-fps X` | 0.001 – 1000 | `2` | frame rate of the frames in the `--video` folder; it sets the time stamps the model sees between frames. Needs `--video` |
| `--video-max-pixels N` | 65536 – 16777216 | `262144` | upper bound on every frame's pixel count after resizing; larger frames are scaled down to fit. More pixels keep more detail and use more memory and context. Needs `--video` |

**Where the weights are looked for**, in this order, stopping at the first complete checkpoint:

1. `--weights DIR`: `DIR` itself, then `DIR/<checkpoint folder name>`. With `--weights` there is no
   fall-through to the places below.
2. `$VZ_WEIGHTS`: itself, then `$VZ_WEIGHTS/<checkpoint folder name>`.
3. `$VEIZIK_CACHE/models/*/*@*/` folders marked ready (the layout `veizik pull` writes).
4. The Hugging Face hub cache (`$HF_HUB_CACHE`, else `$HF_HOME/hub`, else `~/.cache/huggingface/hub`),
   folders `models--<publisher>--<checkpoint folder name>/snapshots/<revision>/`.

A folder counts as the checkpoint only if it is complete: `config.json` matches the selected model's
size and every weight file named by the checkpoint's index is present and non-empty (or a single
non-empty `model.safetensors` exists). Text prompts also need `tokenizer.json` in the folder. The
launcher prints the folder it used (`veizik-run: weights: <dir> (source: …)`). If nothing matches it
lists where it looked and exits 3.

| model key | checkpoint folder name | Hugging Face repository |
|---|---|---|
| `qwen35_0p8b` | `Qwen3.5-0.8B` | `Qwen/Qwen3.5-0.8B` |
| `qwen35_2b` | `Qwen3.5-2B` | `Qwen/Qwen3.5-2B` |
| `qwen35_4b` | `Qwen3.5-4B` | `Qwen/Qwen3.5-4B` |
| `qwen35_9b` | `Qwen3.5-9B` | `Qwen/Qwen3.5-9B` |
| `qwen36_35b_a3b` | `Qwen3.6-35B-A3B` | `Qwen/Qwen3.6-35B-A3B` |

**Output.** `veizik run` writes its output to `gen.txt` in `--out`; for text use `veizik chat` or `veizik serve`.
`run` prints `output: <folder>` when it finishes; progress
lines from the launcher (`veizik-run: …`) go to the terminal. In validation every one-shot run
produced exactly the number of tokens requested; it does not stop early at the end-of-turn token, so
with a chat-formatted prompt trim the text at `<|im_end|>`. Ctrl-C stops a run cleanly (exit 130).

If the device lease is missing or within 3 days of expiring and this machine is an approved device,
`run` first renews it without a browser and says so.

```bash
# image input (Qwen3.6-35B-A3B only); photo.png stands for your own PNG or JPEG
veizik run qwen36_35b_a3b --image photo.png --prompt "What is in this picture?" --out ./out

# chat-formatted prompt, 64 tokens
P=$(printf '<|im_start|>user\nWhat is the capital of France? Answer in one short sentence.<|im_end|>\n<|im_start|>assistant')
VZ_WEIGHTS=/data/models veizik run qwen35_2b "$P" --tokens 64 --out ./out

# long prompt from a file, named mode, explicit weights
veizik run qwen35_9b --prompt-file question.txt --mode balanced --tokens 256 \
    --weights /data/models/Qwen3.5-9B --out ./out
```

### `chat` — interactive session

```
veizik chat <model> [tokens]
```

`chat` opens an interactive prompt in your terminal. It first checks that the model's catalogue entry
declares chat capability (all five models in this package's signed catalogue do), then shows a prompt:
type a message, the engine returns the model's reply as **text**, and the prompt comes back for the
next message. Each line you type is wrapped as a single user turn in the model's chat format. Inside
the prompt: `/help`, `/clear`, `/stats`, `/model`, and `/exit` (or `/quit`, or end of input) to leave.
Each message is answered on its own: the CLI keeps **no conversation history** between messages, so
`/clear` resets the screen and the session counters, not a remembered conversation. It does not
measure token counts or throughput (`/stats` says so). `chat` has no `--weights` option; set
`VZ_WEIGHTS` (or keep the checkpoint in the Hugging Face cache) as for `run`, and the device must be
activated.

For programs and OpenAI-compatible clients, use `veizik serve <model>` with
`POST /v1/chat/completions` (see `serve` below), which also returns text and supports streaming.
Use `veizik run` for one-shot generation.

### `serve` — OpenAI-compatible HTTP server (loopback)

```
veizik serve <model> [--weights DIR] [--host 127.0.0.1] [--port N] [--max-tokens N]
             [--require-auth (--api-key K | --keyfile F)]
             [--usage-log] [--quota-policy FILE [--quota-dir DIR] [--quota-tenants FILE]]
```

On the CUDA runtime `veizik serve` is a launcher: it points the engine at this device's lease, sets
the server on, and hands off to the engine, which loads the model once and answers HTTP itself. It
stays in the foreground; **Ctrl-C** drains and stops it, and the engine's exit code becomes `veizik`'s.

- `<model>` — required here (one of the five model keys). With no model the command exits 2 and lists
  the models. One server hosts one model.
- `--weights DIR` — the checkpoint folder itself. It must contain **both** `tokenizer.json` and
  `tokenizer_config.json`. Without it `serve` looks, in order, at `$VZ_WEIGHTS` (as the checkpoint
  folder itself — not a parent folder) and the `veizik pull` cache `$VEIZIK_CACHE/models/*/*@*/`.
  The Hugging Face hub cache is **not** searched by `serve`. The launcher then re-validates the
  folder against the selected model and refuses a mismatch.
- `--port N` — 1–65535, default `8000`. If the port is not open within about 120 s the command says
  the model is still loading and keeps waiting; poll `GET /readyz` before sending traffic.
- `--host` — accepts only `127.0.0.1` or `localhost`; anything else is refused. The server is not
  reachable from other machines (see [`USAGE_GUIDE.md`](USAGE_GUIDE.md) §2 for exposing it).
- `--max-tokens N` — parsed and range-checked (positive integer) but **not applied** by the CUDA
  server in this release. Set `max_tokens` in each request.
- `--require-auth (--api-key K | --keyfile F)` — require a bearer API key on every request (see
  "API-key authentication" below). `--require-auth` needs exactly one key source, and a key source
  needs `--require-auth`; either mistake exits 2 before anything starts.
- `--usage-log`, `--quota-policy`, `--quota-dir`, `--quota-tenants` — parsed (the quota files are
  validated) but **not applied** by the CUDA server in this release: it has no usage ledger and no
  per-tenant quotas. See "Server front-ends and ledgers".
- When ready it prints `veizik serve: <model> is serving on http://127.0.0.1:<port>` and the two
  completion endpoints.

Endpoints: `GET /v1/models`, `POST /v1/chat/completions`, `POST /v1/completions`, plus `GET /health`,
`/healthz`, `/readyz`, `/metrics`. **Chat completions are supported for all five models** (the signed
model catalogue shipped in the package declares chat capability for each): the server applies the
model's chat template and supports server-sent-event streaming. Request and response details,
streaming, limits and the rejected fields are in [`USAGE_GUIDE.md`](USAGE_GUIDE.md) §2.

#### API-key authentication

```bash
# create a key (8–256 printable ASCII characters, no spaces) in a file only you can read
( umask 077; head -c 24 /dev/urandom | od -An -tx1 | tr -d ' \n' > ~/.veizik-serve.key )

veizik serve qwen35_2b --weights /data/models/Qwen3.5-2B --require-auth --keyfile ~/.veizik-serve.key

curl -s http://127.0.0.1:8000/v1/models                                              # → 401
curl -s http://127.0.0.1:8000/v1/models -H "Authorization: Bearer $(cat ~/.veizik-serve.key)"   # → 200
```

- `--keyfile F` reads the **first line** of `F` (trailing CR, LF and spaces trimmed). **Prefer it:**
  `--api-key K` puts the key on the `veizik serve` command line, where any local user can read it
  with `ps`. With either source the CLI hands the key to the engine through its environment
  (`SV_API_KEY`), never on the engine's command line, and never prints it.
- The key must be 8–256 printable ASCII characters with no spaces; anything else exits 2 (`--api-key/--keyfile must
  be 8..256 printable ASCII bytes, no spaces`, or `--keyfile could not be read, or is empty`).
- With the key on: a request with no key or a wrong key answers **HTTP 401**, error code
  `invalid_api_key`, header `WWW-Authenticate: Bearer`; `Authorization: Bearer <key>` is served
  normally (200). It applies to `/v1/chat/completions`, `/v1/completions` and `/v1/models`.
  `/health`, `/healthz` and `/readyz` are probe endpoints and stay open; `/metrics` requires the key.
- It is one shared key for the whole server process, not a per-user key store (`veizik keys` is not
  used here). Without `--require-auth` the server has no authentication — it is reachable by any
  local process on the machine.
- The server is **loopback-only**: `--host` accepts only `127.0.0.1` or `localhost`, and any other
  address (for example `0.0.0.0`) is refused with exit 2. To reach it from other machines, run a
  reverse proxy on the same host that terminates TLS and forwards to `127.0.0.1:<port>` (keep the
  key on, and send it from the proxy or pass the client's `Authorization` header through). See
  [`USAGE_GUIDE.md`](USAGE_GUIDE.md) §2.

Exit codes: `2` no model / invalid model name / unknown option / bad or misplaced API-key option;
`3` weights not found; `6` the package has no launcher or is not a text bundle; otherwise the
engine's code (`4` integrity or GPU modules, `70`/`74` activation).

```bash
veizik serve qwen35_2b --weights /data/models/Qwen3.5-2B --port 8000
curl -s http://127.0.0.1:8000/v1/chat/completions -H 'content-type: application/json' \
     -d '{"model":"qwen35_2b","messages":[{"role":"user","content":"Hello"}],"max_tokens":32}'
```

### `ps` / `stop` — resident servers

```
veizik ps
veizik stop <port> | all
```

These list and stop servers started by the CLI's own request front. The CUDA server is not started
that way: `ps` prints `No resident server is running here.` and `stop` reports that it found no running server to stop, so
**`veizik stop` does not close a server you started detached** (in the background, under `nohup`,
`tmux` or a supervisor). Stop the CUDA server with Ctrl-C in its terminal: the signal reaches the
engine, which drains in-flight requests and exits. For a detached server, find the engine process
that is listening on the port (`ss -ltnp | grep :8000`) and `kill` it, or signal the whole process
group of the `veizik serve` process. (`POST /shutdown` and `POST /restart` answer 403 on this
server.)

---

## Get and manage models

### `models` — list the models in this package

```
veizik models
```

Lists the models of this package with four columns: `MODEL` (the key every command takes), `NAME`
(the catalogue's name), `TIER` (the catalogue's own status label for the model, `EXPERIMENTAL` for all
five in this release) and `ON DISK`. `ON DISK` is a per-model status label: `ready` when a model's
weights sit inside the install, `incomplete (no weights)` when they do not. This package keeps the
weights outside the install, so every row reads `incomplete (no weights)` even when `veizik run`
works — it is a label, not a sign of a broken command. Use `models` to see the model keys, not to
check readiness.

### `pull` — the CLI's model downloader

```
veizik pull <model>[@<revision>] [--profile P] [--offline] [--quiet]
```

`pull` is the CLI's downloader (it resolves model names against the signed catalogue, downloads into
a local cache, and honours `--offline`). For this package it has nothing to fetch from: it
reports "`veizik pull` cannot fetch weights for this package yet" and tells you to download the
model's Hugging Face snapshot yourself and point Veizik at it with `--weights DIR` or `VZ_WEIGHTS`
([`README.md`](README.md) §2, "Model weights").

### `hf` — Hugging Face token

```
veizik hf login | logout | status
```

`login` reads the token from standard input (never from the command line): `printf %s "$HF_TOKEN" |
veizik hf login`. The token is used by `pull` for gated repositories; it has no effect on this package.

### `remove` — delete from the download cache

```
veizik remove <model>[@<revision>]
```

Removes a model (or one revision) from the **download cache**. It never touches the installed
package or the weights you supplied.

### `convert` — a checkpoint checker (no converter in this release)

```
veizik convert <source> [-o <file>] [--profile fastest|balanced|quality|smallest|auto]
```

`<source>` is a local checkpoint folder (or the name of a model you have already downloaded).
`convert` is a real checker: it reads the checkpoint's `config.json`, confirms that the architecture is
one this installation accepts, and checks that weights and a `tokenizer.json` are present, printing a
short report (Source, Target, Architecture, Support, Weights, Tokenizer). This release ships no
converter, so it writes no model file — it reports that the checkpoint is accepted and nothing was
written. Nothing needs converting: `veizik run` reads a Hugging Face checkpoint as it is.

### `inspect` — what a model is

```
veizik inspect <model> [--json]
```

A real verb that shows what is known about a model: its catalogue status, the context window this
runtime supports, and whether it can run here (`--json` prints the same items for scripts). On this
package the weights live outside the install, so `inspect` reports that the model cannot run because
its weights are missing; it shows the full model information when the runtime and weights are
present where the CLI looks for them.

---

## Look after the installation

### `bench` — time this machine

```
veizik bench <model> [--prompt-tokens N] [--generate N] [--profile auto]
```

- `--prompt-tokens N` — length of the synthetic prompt (default 16, maximum 4096).
- `--generate N` — accepted and range-checked (minimum 8, maximum 100000) but **not used** on this
  package.
- `--profile auto` — the only profile value accepted.
- On this package `bench` runs `veizik run <model>` three times with the synthetic prompt and default
  settings (`balanced`, 128 tokens) and reports the **median end-to-end time** of the whole
  invocation, model load included. The prefill, first-token, decode and memory rows print `—`; the
  command's own usage text describes a seven-run method used on other platforms. Weights and an
  activated device are required, as for `run`; the weights are found by the same search as `run`
  through `$VZ_WEIGHTS`, `$VEIZIK_CACHE` and the Hugging Face cache (`bench` takes no `--weights`).
- To measure decode tok/s, use the per-run timing lines the engine prints (method in
  [`bench/REPRODUCIBILITY.md`](bench/REPRODUCIBILITY.md)).

```bash
VZ_WEIGHTS=/data/models veizik bench qwen35_9b --prompt-tokens 16
```

### `cache` — the download cache

```
veizik cache info
veizik cache clean [--all]
```

Manages the `veizik pull` cache, which this package does not use. `clean` removes interrupted
download work; `--all` also removes completed models. It does not touch the installed package or
your weights.

### `config` — settings

```
veizik config show
veizik config set <key> <value>
veizik config unset <key>
veizik config path
```

Keys: `cache.path`, `default.model`, `default.profile`, `offline`, `activation.host`, `license.id`,
`serve.allowed_origins`. For this package only `activation.host` (the activation service address,
normally not needed) and `license.id` (filled in automatically by activation) matter. The settings
file is `${XDG_CONFIG_HOME:-~/.config}/veizik/config.json`; an environment variable wins over the file.

### `completion` — shell completion

```
veizik completion zsh | bash | fish
```

Prints a completion script:

```bash
veizik completion bash > /usr/local/etc/bash_completion.d/veizik
veizik completion zsh  > "${fpath[1]}/_veizik"
veizik completion fish > ~/.config/fish/completions/veizik.fish
```

Model-name completion asks `veizik models`.

`quota`, `usage` and `audit` are described under "Server front-ends and ledgers" below.

---

## Device, activation, health

### `status` — this device's activation

```
veizik status
```

```
release     <engine folder name>
activation  activated · this device          (or: not activated · veizik activate | expired · veizik activate)
expires     in N days · valid                (or: N days ago · expired | … · in grace — renew)
files       device key + lease + key blob present      (or tells you what is missing)
```

Exit `0` valid · `1` in the renewal grace period (run `veizik activate`) · `4` not activated or
expired · `6` no engine at the install root. `status` reads the lease; the runtime checks its
signature, release and device binding at every run.

### `activate` — bind this device

```
veizik activate                                   # approve the printed address and code in a browser
veizik activate --key KEY [--password-stdin]      # browser-free
veizik activate --refresh                         # renew the lease only
```

| option | meaning |
|---|---|
| *(none)* | browser approval: prints an address and a code, tries to open a browser (if none opens, open the printed address on any device), and waits up to about ten minutes |
| `--no-browser` | do not open a browser; print the address only |
| `--key KEY`, `-k KEY` | browser-free activation with a key from your account page (`-` reads `VEIZIK_ACTIVATION_KEY`; `file:PATH` reads the first line of `PATH`). A mistyped key (keys start with `vzek_`) is rejected locally before anything is sent |
| `--email ADDR` | browser-free with your account e-mail and CLI password (may e-mail a 6-digit code); not combinable with `--key` |
| `--password-stdin` | read the CLI password from standard input (recommended) |
| `--password-file PATH` | read it from the first line of `PATH` |
| `--password PW`, `-p PW` | on the command line (visible to `ps` and shell history); `-p` alone asks |
| `--no-password` | the key needs no password |
| `--code CODE` | the 6-digit e-mail code, if you already have it |
| `--refresh` | renew the lease only; never opens a browser; exit 5 if this machine is not approved or the renewal fails |
| `--reapprove` | ask for a new approval even if this machine is already approved |

Give the CLI password one way only (12–128 printable ASCII characters). `--token` (headless
enrolment) is **not available in this release** and is refused (exit 2); `--license` is no longer
accepted. `veizik activate --help` prints this help and exits 2.

Activation ends with one short check generation using `qwen35_0p8b`, so that model's weights must be
on this machine ([`README.md`](README.md) §2, "Model weights"). Without them activation installs the lease, reports that the device is
**not confirmed** (exit 6), and tells you to get the weights and run `veizik activate` again.
Exit `0` activated · `2` usage / bad key, e-mail or code · `5` `--refresh` failed · `6` the service
refused, install failed, or the check generation did not confirm the device · `130` interrupted.

```bash
printf '%s' "$CLI_PASSWORD" | veizik activate --key vzek_… --password-stdin
```

### `deactivate` — release this device

```
veizik deactivate [--forget]
```

Frees this device's slot on your account and deletes its lease files. `--forget` also deletes the
device key (for a container or VM you are about to discard); the next activation then registers a new
device. Needs the network. Exit `0` · `2` · `6`.

### `devices` — the devices on your licence

```
veizik devices                  # list
veizik devices disable          # hand THIS device back; frees its slot (the lease stays until it expires)
veizik devices enable           # let THIS device run again
```

It can only switch the machine it runs on; to turn off a machine you no longer have, use your
account page. Needs an activated device. Exit `0` · `2` · `6`.

### `doctor` — check this installation

```
veizik doctor
```

Reports `root`, `backend`, the activation service address (and where it was configured), the
model catalogue (shipped with this package: `present · signature verified`), the integrity of the CLI
binary, the lease helper state, and a final `status ready`. Exit `0`; `6` when no engine is found (set `VEIZIK_ROOT`). It does
**not** check your GPU, driver, weights or lease — use `nvidia-smi` and `veizik status` for those.

### `device-id` — there is no such command

The shipped CLI has no `device-id` command (it is rejected as an unknown command). Use
`veizik devices` to list the devices on your licence (this one included), and `veizik status` for
this device's activation state.

### `version`

```
veizik version        # veizik 1.2.0 · runtime native · backend CUDA
```

Also `--version`, `-v`, `-V`. The CLI version is numbered separately from the package version
(`1.1.0`).

---

## Server front-ends and ledgers

`keys`, `usage`, `audit`, `quota` and `gateway` are real, standalone local CLI tools — not stubs — and
they run normally. They were built around a request front (a key store, a usage ledger, per-tenant
quotas) that is **not integrated with the CUDA server**: the engine answers HTTP itself. Its API-key
check is the single shared key of `serve --require-auth` (above); there is no in-serve usage ledger,
quota enforcement or key store. So `keys`, `usage`, `audit` and `quota` manage local files that the
CUDA server never reads, and `serve --usage-log` / `--quota-*` are not applied. You can still use the
tools on their own (for example to keep a usage ledger fed by your own proxy). `gateway` was not
exercised against the CUDA server in this release's validation.

### `keys` — API keys and SSO trust

```
veizik keys create [--label L] [--scope a,b] [--models m1,m2|*] [--tenant T] [--expires-in SECS]
veizik keys list
veizik keys revoke <id>
veizik keys rotate <id> [--grace SECS]
veizik keys verify [--endpoint E] [--model M] [--now T]     # credential read from $VEIZIK_KEY
veizik keys oidc set --jwks FILE [--iss I] [--aud A] [--scope a,b] [--models m] [--tenant T]
veizik keys oidc show | clear
```

Keys look like `vzk_<id>_<secret>`; the secret is shown once and only a keyed hash is stored.
Scopes: `chat`, `completions`, `models`, `embeddings`, `metrics`, `admin`, `*` (default
`chat,completions,models`). `verify` answers allowed/denied for a credential, endpoint class and
model, which a proxy of your own can call.

### `usage` / `audit` — tamper-evident usage ledger

```
veizik usage record --key K --tenant T --model M --prompt-tokens N --completion-tokens N --latency-ms N --status S
veizik usage record --batch FILE
veizik usage report --since S [--until U] [--by key|model|tenant] [--format csv|json]
veizik usage rotate [--actor A]
veizik audit verify [--expect-head SEQ:HASH]
veizik audit head
veizik audit admin --actor A --action X [--target T]
veizik audit repair [--actor A]
veizik audit reset --confirm --actor A
```

An append-only, hash-chained ledger of counts (never prompts or responses). `--since`/`--until`
take epoch seconds, `YYYY-MM-DD`, or `Nd`/`Nh`/`Nm`. The chain is tamper-evident: it shows a change but cannot prevent one;
pin `audit head` off the machine and check it with `audit verify --expect-head`.

### `quota` — per-tenant limits

```
veizik quota check <policy> [<tenants>]
veizik quota show <policy> <state-dir>
veizik quota tenant add|list|remove <tenants-file> [<tenant>]
```

Validates a tenant policy file, shows usage from a state directory, and manages the file that maps
bearer tokens to tenants (a token is printed once; only its hash is stored).

### `gateway` — TLS and token front

```
veizik gateway [--listen ADDR] [--port N] [--upstream PORT] [--tls-cert FILE --tls-key FILE]
               [--auth-file FILE | --no-auth] [--allow CIDR]... [--cors ORIGIN]...
               [--max-conns N] [--max-conns-per-ip N] [--max-body BYTES]
               [--request-timeout SECS] [--idle-timeout SECS] [--reload-interval SECS]
               [--insecure-plain] [--forward-auth]
```

A single-process HTTP/1.1 front for a loopback server: TLS 1.3 (ECDSA P-256 certificates), bearer
tokens checked against a file of SHA-256 digests, IP allow-list, CORS. Defaults: listen `127.0.0.1`,
`--port 8080`, `--upstream 8000`, `--max-body 1048576`, `--request-timeout 15`, `--idle-timeout 120`,
`--max-conns 256`, `--max-conns-per-ip 64`, `--reload-interval 300`. A non-loopback `--listen`
requires TLS (or `--insecure-plain`) and authentication (`--auth-file`, or `--no-auth`); otherwise it
refuses to start. `--auth-file` holds one 64-hex SHA-256 digest of a token per line (at most 256).
It streams responses, including server-sent events. It has no HTTP/2, keep-alive, IPv6 or client
certificates. It is not specific to one engine, but it has not been exercised against the CUDA
server in this release's validation.

```bash
printf '%s' "$TOKEN" | sha256sum | cut -d' ' -f1 > tokens.sha256
veizik gateway --listen 0.0.0.0 --port 8443 --upstream 8000 \
    --tls-cert cert.pem --tls-key key.pem --auth-file tokens.sha256 --allow 10.0.0.0/8
```

### `cluster` — route over several servers

```
veizik cluster run [--config FILE] [--require-auth]
veizik cluster check [--config FILE]
veizik cluster status [--port N]
veizik cluster reload [--port N] [--roll]
veizik cluster stop [--port N]
veizik cluster keys add <tenant> | list | revoke <id|tenant>   [--file F]
```

A router that spreads requests over several `veizik serve` ports from a line-oriented config file
(`listen`, `backend host:port [models=…] [slots=N] [spawn=<model>]`, health and timeout settings,
`auth_file`). It probes each backend's `GET /ready`, retries only requests that never reached a
backend, and can supervise the servers it starts. `cluster check` validates a config. It has not
been exercised against the CUDA server in this release's validation.

### `service` — run `serve` as a systemd user service

```
veizik service print|install|uninstall|status|logs|rotate [--name N] [--port N] [--bin PATH] [--model TAG] [--no-start] [--lines N]
```

Writes a `systemctl --user` unit that runs `veizik serve <model> --port N`. The unit carries no
weights location and no environment, so on this package the service can find weights only in the
`veizik pull` cache, which this package cannot fill; `service install` is therefore not usable here
in this release. `service rotate` is not supported on Linux (journald owns the logs).

---

## Environment variables

| variable | effect |
|---|---|
| `VEIZIK_ROOT` | the engine folder the CLI uses (the `veizik` command from `install.sh` sets it for you) |
| `VZ_WEIGHTS` | where to look for model weights (`run`, `bench`, `serve`, and the activation check) |
| `VEIZIK_CACHE` | the `veizik pull` cache root, searched by `run` and `serve` |
| `HF_HUB_CACHE`, `HF_HOME` | where the Hugging Face cache lives (searched by `run` and `bench`) |
| `VEIZIK_OUT` | default output folder for `run` and scratch folder for the CLI (else `~/veizik-out`) |
| `Q35_SEAL_ARCH` | only if `nvidia-smi` is unavailable or your GPUs differ: one of `sm80`, `sm86`, `sm89`, `sm90a`, `sm100a`, `sm120a` |
| `VEIZIK_ACTIVATION_KEY` | read by `activate --key -` |
| `VEIZIK_ACTIVATION_PASSWORD` | CLI password source when no password option is given (`--password-stdin` is safer) |
| `VEIZIK_ACTIVATION_EMAIL` | read by `activate --email -` |
| `VEIZIK_ACTIVATION_HOST` | overrides the activation service address (normally not needed) |
| `VEIZIK_LEASE_DAEMON` | set to `0` to use a per-run lease instead of the RAM-only lease helper |
| `VEIZIK_KEY` | the credential `keys verify` checks |
| `XDG_STATE_HOME`, `XDG_CONFIG_HOME` | where activation state and settings are kept |
| `NO_COLOR` | turn off coloured output |

Veizik does not read model credentials from the environment for generation, and generation makes no
network calls; only activation, lease renewal and `pull`/`hf` use the network.

---

## One-screen cheat-sheet

```bash
veizik version                                  # CLI version + backend
export VZ_WEIGHTS=/data/models                  # folder holding Qwen3.5-0.8B/, Qwen3.5-9B/, …
veizik activate                                 # register this device (once; needs the 0.8B weights)
veizik status                                   # activation, expiry
veizik run qwen35_9b "…" --mode balanced        # generate once; output in ~/veizik-out/gen.txt
veizik chat qwen35_2b                           # interactive session in the terminal (/exit leaves)
veizik serve qwen35_2b --weights $VZ_WEIGHTS/Qwen3.5-2B   # OpenAI-compatible server on 127.0.0.1:8000
veizik bench qwen35_9b                          # time this machine (3 end-to-end runs)
veizik deactivate [--forget]                    # release this machine
veizik doctor                                   # check the install
```
