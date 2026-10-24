# veizik CLI — Complete Command Reference (CUDA / Linux, CLI 1.4.3)

Every command the shipped `veizik` binary accepts, its flags, exit codes and a worked example. This
reference matches CLI 1.4.3, which serves the Qwen package (`veizik-qwen-cuda 1.1.0`) and the WAN
package (`veizik-wan 1.2.0`) with **one common set of commands**. A flag appears here only if the
binary accepts it. Where a command is present but has a narrower role for these packages (for example
it works on the CLI's own local files), the entry says so. Exit codes are listed for the commands where
they matter to a script; for the rest the entry describes what the command does and prints.

The installer puts one command on your `PATH`: `veizik`. No `vz` alias is installed by this package;
add `alias vz=veizik` yourself if you want the short form.

Built-in help: `veizik --help` (also `-h`, `help`) prints the command summary and exits 0; `veizik`
with no arguments prints it and exits 2. `veizik <command> --help` prints the detail of one command.
`veizik version` prints the CLI version and backend; `veizik doctor` checks the installation. A command
given missing or unknown arguments prints its own usage and exits 2. Unknown or mistyped options are
errors, never ignored.

```
veizik <command> [arguments]
```

## The common command set

Every engine answers the same verbs. Only the accepted `run` flags (see `run`) and the shape of the
`serve` API differ between the language models and the video models.

| group | command | what it does |
|---|---|---|
| use a model | `run <model> "<prompt>" [tokens]` | generate once and exit |
| | `chat <model> [tokens]` | an interactive session |
| | `serve [<model>] [--port N]` | answer over HTTP, locally (omit the model = all installed) |
| | `ps` | list the resident servers running here |
| | `stop <port> \| all` | stop a resident server |
| get and manage models | `models` | list what is installed here |
| | `list` | model engines: installed and available |
| | `install <model>` | download and install a model engine |
| | `update [<model>]` | update installed engine(s) to the newest — **not functional yet** |
| | `uninstall <model>` / `rm <model>` | remove an installed model engine |
| | `pull <model>[@<revision>]` | fetch model weights and make them ready |
| | `hf login \| logout \| status` | the Hugging Face token for gated models |
| | `remove <model>[@<revision>]` | delete cached weights |
| | `convert <source> [-o <file>]` | prepare a checkpoint — **not functional yet** (no converter) |
| | `inspect <model>` | show what a model is |
| look after the installation | `bench <model>` | measure this machine |
| | `cache info\|clean` | inspect or tidy the download cache |
| | `config show\|set\|unset` | see and change settings |
| | `completion zsh\|bash\|fish` | emit a shell completion script |
| | `status` | show this device's activation and plan |
| | `activate` | register this device and get its plan (browser approval; one approval covers all models) |
| | `devices [enable\|disable <tag>]` | see and switch the devices on your licence |
| | `device-id` | print this machine's device id (matches the website list) |
| | `doctor` | check this installation |
| | `version` | show version and backend |

**Generation needs two things.** `run`, `chat` and `serve` generate only on a device activated with
`veizik activate` **and** with the model weights present (`--weights DIR` where the command takes it, `VZ_WEIGHTS`,
or the `veizik pull` cache). Before that they stop with exit 70 (not activated) or exit 3 (weights not found).

`update` and `convert` exist as commands but do nothing useful yet: `update` does not refresh the
catalogue, and `convert` has no converter. Do not build scripts on them.

## Exit codes (shared across verbs)

| code | meaning |
|---|---|
| `0` | success |
| `1` | `run`/`serve`: the engine failed, or finished without confirming the configuration it ran in (the result is not what you asked for); `status`: the lease is in its renewal grace period |
| `2` | usage error: no args, unknown command, unknown or invalid option, missing or blank argument, out-of-range value, unknown model or mode; a `run` flag the selected engine does not accept (`<flag> does not apply to this model.`); for `run`/`serve` also: the engine refused the model configuration, or the GPU generation could not be read (set `Q35_SEAL_ARCH`); image or video input that cannot be used (wrong model, more than one image or video, `--image` with `--video`, no text prompt, an unsupported or damaged file, frames of different sizes or fewer than 2 / more than 256, over the size or aspect-ratio budget) |
| `3` | an input is missing or unreadable: model weights, tokenizer, the image file, the video frames folder, or the output folder cannot be created |
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
veizik run <model> "<prompt>" [tokens] [options]
```

- `<model>` — a model key (Qwen: `qwen35_0p8b`, `qwen35_2b`, `qwen35_4b`, `qwen35_9b`,
  `qwen36_35b_a3b`; WAN: `wan21_t2v_1_3b`, `wan21_t2v_14b`, `wan22_t2v_a14b`, `wan22_i2v_a14b`). The
  model's package must be installed (`veizik install`); `run` finds the installed engine itself.
- The prompt is the quoted second argument. For a long or private prompt, put it in a file and pass
  `"$(cat question.txt)"`. For a language model, a bare number after the prompt is the token count.
- Options are written `--name value` and may follow the prompt. An unknown option stops the run with
  exit 2 and nothing is executed.

**One flag vocabulary, translated per engine.** You write one set of flags; the CLI forwards to each
engine only the flags that engine accepts. A flag the selected engine does not accept is refused
before anything runs, with `<flag> does not apply to this model.`

Flags valid for every model:

| option | meaning |
|---|---|
| `--out DIR` | where the render is saved: an absolute folder, created if missing (default `$VEIZIK_OUT`, else `~/veizik-out`). It must be outside the installed engine folder |
| `--name NAME` | name this run; it is saved as `<out>/<NAME>` (letters, digits, `.` `_` `-`) |
| `--resume` | resume this run from its own checkpoint |
| `--resume-from REF` | resume **that run's** folder (`REF` is a `--name`, or an absolute folder); it reloads `work/s4.ckpt` there. It is not `--extend` |
| `--checkpoint-every N` | write a resume checkpoint every N steps |
| `--vzq FILE` | load weights from a sealed `.vzq` file instead of a checkpoint |

**Accepted per engine.** Flags outside the engine's set are refused.

| engine | accepted run flags |
|---|---|
| Qwen (Qwen3.5 / Qwen3.6 language) | `--seed` `--steps` `--mode` `--temperature` `--top-p` `--top-k` `--tokens` `--max-tokens` `--ignore-eos` `--image` `--video` `--image-max-pixels` `--video-fps` `--video-max-pixels` |
| WAN (Wan2.1 / Wan2.2 video) | `--steps` `--frames` `--width` `--height` `--seed` `--checkpoint-every` `--png-step` `--guidance` `--guidance2` `--shift` `--lora-scale` `--mode` `--det-vae` `--image` `--lora` `--neg-file` |

**Qwen flags**

| option | value | default | meaning |
|---|---|---|---|
| `--tokens N`, `--max-tokens N` | whole number (1 – 4096) | `128` | generation length; `--steps N` means the same; a bare number after the prompt is the same too |
| `--ignore-eos` | *(no value)* | off | emit exactly N tokens instead of stopping at end-of-turn |
| `--mode M` | `quality` · `balanced` · `fast` · `ultrafast` · `low-memory` | `balanced` | quality / memory / speed preset (see [`USAGE_GUIDE.md`](USAGE_GUIDE.md) §5) |
| `--temperature X` | 0 – 2 | `0` (greedy) | sampling temperature — **experimental** |
| `--top-p X` | 0 – 1 | — | nucleus threshold — **experimental** |
| `--top-k N` | 0 – 1000 | — | top-k — **experimental** |
| `--seed N` | whole number | — | sampling seed — **experimental** |

Sampling (`--seed`, `--temperature`, `--top-p`, `--top-k`) is opt-in; greedy decoding is the default.

**Image and video input (Qwen3.6-35B-A3B only).** These flags apply to `qwen36_35b_a3b`; the other
Qwen models take text only.

| option | value | default | meaning |
|---|---|---|---|
| `--image FILE` | PNG or JPEG | — | an image the model looks at; exactly one per run; applies the chat template (the answer ends at the end-of-turn token) |
| `--image-max-pixels N` | 65536 – 16777216 | `1048576` | upper bound on the image's pixel count after resizing; a larger image is scaled down to fit. Needs `--image` |
| `--video DIR` | folder of PNG or JPEG frames | — | 2 to 256 frames, all the same size, in file-name order (= time order); one video per run; not with `--image`; applies the chat template |
| `--video-fps X` | 0.001 – 1000 | `2` | frame rate of the frames in the `--video` folder; it sets the time stamps the model sees between frames. Needs `--video` |
| `--video-max-pixels N` | 65536 – 16777216 | `262144` | upper bound on every frame's pixel count after resizing. Needs `--video` |

```bash
veizik run qwen36_35b_a3b "What is in this picture?" --image photo.png
veizik run qwen36_35b_a3b "What happens in this clip?" --video ./frames --video-fps 2
```

On a GPU the image and video stage does not support, the run is refused cleanly with code 50 (`the image stage refused this request (status 50)`) before any image or video work. Usage and limits: [`USAGE_GUIDE.md`](USAGE_GUIDE.md) §1a.

**WAN flags** (video models; the full meaning of each is in [`wan/README.md`](wan/README.md) §4)

| option | meaning |
|---|---|
| `--steps N` · `--frames N` · `--width W` · `--height H` | denoise steps, frame count, render size |
| `--seed N` | noise seed |
| `--guidance G` · `--guidance2 G2` · `--shift S` | classifier-free guidance (`--guidance2` is the low-noise expert of the two-expert models) and flow shift |
| `--mode M` | render mode: `quality` · `balanced` · `fast` · `ultrafast` |
| `--png-step N` | write every N-th frame as PNG |
| `--det-vae yes` | deterministic VAE encode and decode |
| `--image FILE` | first frame, for image-to-video |
| `--neg-file FILE` | negative prompt from a file |
| `--lora FILE`, `--lora-scale X` | accepted by the CLI; LoRA is not supported in this release, do not rely on it |
| `--checkpoint-every N` | checkpoint every N steps (listed above) |

```bash
veizik run wan22_t2v_a14b "A red car driving along a coastal road at sunset." --out $HOME/clip --steps 40 --seed 7
veizik run wan22_t2v_a14b "A red car driving along a coastal road at sunset." --out $HOME/clip --resume   # after an interruption
```

`--vzq` loads sealed `.vzq` weights; `--resume-from REF` resumes the folder `REF`, not a new run.

**Where the weights are looked for** (Qwen), in this order, stopping at the first complete checkpoint:

1. `$VZ_WEIGHTS`: itself, then `$VZ_WEIGHTS/<checkpoint folder name>`.
2. `$VEIZIK_CACHE/models/*/*@*/` folders marked ready (the layout `veizik pull` writes).
3. The Hugging Face hub cache (`$HF_HUB_CACHE`, else `$HF_HOME/hub`, else `~/.cache/huggingface/hub`),
   folders `models--<publisher>--<checkpoint folder name>/snapshots/<revision>/`.

A folder counts as the checkpoint only if it is complete: `config.json` matches the selected model's
size and every weight file named by the checkpoint's index is present and non-empty (or a single
non-empty `model.safetensors` exists). Text prompts also need `tokenizer.json` in the folder. The
launcher prints the folder it used (`veizik-run: weights: <dir> (source: …)`). If nothing matches it
lists where it looked and exits 3. WAN weights are laid out as described in [`wan/README.md`](wan/README.md) §3.

| model key | checkpoint folder name | Hugging Face repository |
|---|---|---|
| `qwen35_0p8b` | `Qwen3.5-0.8B` | `Qwen/Qwen3.5-0.8B` |
| `qwen35_2b` | `Qwen3.5-2B` | `Qwen/Qwen3.5-2B` |
| `qwen35_4b` | `Qwen3.5-4B` | `Qwen/Qwen3.5-4B` |
| `qwen35_9b` | `Qwen3.5-9B` | `Qwen/Qwen3.5-9B` |
| `qwen36_35b_a3b` | `Qwen3.6-35B-A3B` | `Qwen/Qwen3.6-35B-A3B` |

**Output.** A Qwen `run` writes its text to `gen.txt` in the run folder; a WAN `run` writes PNG frames
to `<run folder>/frames/`. `run` prints `output: <folder>` when it finishes; progress lines from the
launcher (`veizik-run: …`) go to the terminal. The prompt is used **as written**: no chat template is
applied to a text prompt (image and video runs apply it). Ctrl-C stops a run cleanly (exit 130).

If the device lease is missing or within 3 days of expiring and this machine is an approved device,
`run` first renews it without a browser and says so.

```bash
# chat-formatted prompt, 64 tokens
P=$(printf '<|im_start|>user\nWhat is the capital of France? Answer in one short sentence.<|im_end|>\n<|im_start|>assistant')
VZ_WEIGHTS=/data/models veizik run qwen35_2b "$P" --tokens 64 --out $HOME/out

# exactly 256 tokens, a named mode
VZ_WEIGHTS=/data/models veizik run qwen35_9b "Explain attention." --mode balanced --tokens 256 --ignore-eos
```

### `chat` — interactive session

```
veizik chat <model> [tokens]
```

`chat` opens an interactive prompt in your terminal. It first checks that the model's catalogue entry
declares chat capability (all five Qwen models do; a video model has no chat), then shows a prompt:
type a message, the engine returns the model's reply as **text**, and the prompt comes back for the
next message. Each line you type is wrapped as a single user turn in the model's chat format. Inside
the prompt: `/help`, `/clear`, `/stats`, `/model`, and `/exit` (or `/quit`, or end of input) to leave.
Each message is answered on its own: the CLI keeps **no conversation history** between messages, so
`/clear` resets the screen and the session counters, not a remembered conversation. It does not
measure token counts or throughput (`/stats` says so). `chat` has no `--weights` option; set
`VZ_WEIGHTS` (or keep the checkpoint in the Hugging Face cache) as for `run`, and the device must be
activated. `chat` generates only with an activated device and the weights present.

For programs and OpenAI-compatible clients, use `veizik serve <model>` with
`POST /v1/chat/completions` (see `serve` below), which also returns text and supports streaming.
Use `veizik run` for one-shot generation.

### `serve` — answer over HTTP, locally (loopback)

```
veizik serve [<model>] [--weights DIR] [--host 127.0.0.1] [--port N] [--max-tokens N]
             [--require-auth (--api-key K | --keyfile F)]
```

`serve` answers over HTTP on `127.0.0.1` only. With no model named it serves every installed model.
The API depends on the engine, and the verbs, flags and activation are the same:

| engine | what `serve` exposes |
|---|---|
| Qwen (language) | the OpenAI-compatible API: `POST /v1/chat/completions` (streaming supported), `POST /v1/completions`, `GET /v1/models`, plus `GET /health`, `/healthz`, `/readyz`, `/metrics`. Loopback only; `--require-auth` with `--keyfile` requires an API key |
| WAN (video) | a render API: `POST /v1/videos/generations` with `{"prompt","seed"}` renders and answers with a folder of PNG frames; `GET /health`; `GET /v1/models`. A resident render server runs underneath, so the model stays loaded between requests |

Both need `veizik activate` and the model weights before they generate; until the device is activated
a request is refused (HTTP 403 / exit 70).

On the CUDA runtime `veizik serve` is a launcher: it points the engine at this device's lease, sets
the server on, and hands off to the engine, which loads the model once and answers HTTP itself. It
stays in the foreground; **Ctrl-C** drains and stops it, and the engine's exit code becomes `veizik`'s.
A resident server is listed by `veizik ps` and stopped by `veizik stop <port>` or `veizik stop all`.

- `--weights DIR` — the checkpoint folder itself. For Qwen it must contain **both** `tokenizer.json`
  and `tokenizer_config.json`. Without it `serve` looks, in order, at `$VZ_WEIGHTS` (as the
  checkpoint folder itself — not a parent folder) and the `veizik pull` cache
  `$VEIZIK_CACHE/models/*/*@*/`. The Hugging Face hub cache is **not** searched by `serve`. The
  launcher then re-validates the folder against the selected model and refuses a mismatch.
- `--port N` — 1–65535, default `8000`. If the port is not open within about 120 s the command says
  the model is still loading and keeps waiting; poll `GET /readyz` (Qwen) before sending traffic.
- `--host` — accepts only `127.0.0.1` or `localhost`; anything else is refused. The server is not
  reachable from other machines (see [`USAGE_GUIDE.md`](USAGE_GUIDE.md) §2 for exposing it).
- `--max-tokens N` — parsed and range-checked (positive integer) but **not applied** by the CUDA
  server in this release. Set `max_tokens` in each request.
- `--require-auth (--api-key K | --keyfile F)` — require a bearer API key on every request (see
  "API-key authentication" below). `--require-auth` needs exactly one key source, and a key source
  needs `--require-auth`; either mistake exits 2 before anything starts.
- When ready it prints `veizik serve: <model> is serving on http://127.0.0.1:<port>`.

Qwen endpoints: `GET /v1/models`, `POST /v1/chat/completions`, `POST /v1/completions`, plus `GET /health`,
`/healthz`, `/readyz`, `/metrics`. **Chat completions are supported for all five models**: the server applies the
model's chat template and supports server-sent-event streaming. Request and response details,
streaming, limits and the rejected fields are in [`USAGE_GUIDE.md`](USAGE_GUIDE.md) §2. The WAN render
API is described in [`wan/README.md`](wan/README.md) §8.

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
- It is one shared key for the whole server process, not a per-user key store. Without `--require-auth` the server has no authentication — it is reachable by any
  local process on the machine.
- The server is **loopback-only**: `--host` accepts only `127.0.0.1` or `localhost`, and any other
  address (for example `0.0.0.0`) is refused with exit 2. To reach it from other machines, run a
  reverse proxy on the same host that terminates TLS and forwards to `127.0.0.1:<port>` (keep the
  key on, and send it from the proxy or pass the client's `Authorization` header through). See
  [`USAGE_GUIDE.md`](USAGE_GUIDE.md) §2.

Exit codes: `2` invalid model name / unknown option / bad or misplaced API-key option;
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

`ps` lists the resident servers running on this machine; `stop <port>` stops the server on that port
and `stop all` stops every server this user runs. A foreground `veizik serve` can also be stopped
with Ctrl-C in its terminal: the signal reaches the engine, which drains in-flight requests and
exits. (`POST /shutdown` and `POST /restart` answer 403 on the Qwen server.)

---

## Get and manage models

### `models` — list what is installed here

```
veizik models
```

Lists the models of the installed packages with four columns: `MODEL` (the key every command takes),
`NAME` (the catalogue's name), `TIER` (the catalogue's own status label for the model, `EXPERIMENTAL`
for the five Qwen models in this release) and `ON DISK`. `ON DISK` is a per-model status label:
`ready` when a model's weights sit inside the install, `incomplete (no weights)` when they do not.
These packages keep the weights outside the install, so a row can read `incomplete (no weights)` even
when `veizik run` works — it is a label, not a sign of a broken command. Use `models` to see the model
keys, not to check readiness.

### `list` — model engines: installed and available

```
veizik list
```

Shows each model engine and whether it is installed here or available to install.

### `install` — download and install a model engine

```
veizik install <model>
```

`<model>` is a keyword. It is case-insensitive, and `.` or `-` stand for `_`:

| package | keywords |
|---|---|
| Qwen (release `v1.1.0`) | `qwen`, `qwen35`, `qwen36`, or a model key: `qwen35_0p8b`, `qwen35_2b`, `qwen35_4b`, `qwen35_9b`, `qwen36_35b_a3b` |
| WAN (release `v1.2.0`) | `wan`, `wan21`, `wan22`, or a model key: `wan21_t2v_1_3b`, `wan21_t2v_14b`, `wan22_t2v_a14b`, `wan22_i2v_a14b` |

`install` downloads the package anonymously from this repository's release, refuses it if its sha256
differs from the published release digest, and extracts it to
`${XDG_STATE_HOME:-~/.local/state}/veizik/engines/<model>/`. It refuses to run on macOS. After
`install`, `run`, `chat` and `serve` find the engine themselves; no `VEIZIK_ROOT` is needed.

### `update` — not functional yet

```
veizik update [<model>]
```

The command exists, but the catalogue refresh it needs is not available yet, so it does not update
anything. To get a newer package, install it again with `veizik install <model>`.

### `uninstall` / `rm` — remove an installed engine

```
veizik uninstall <model>
veizik rm <model>
```

`rm` is an alias for `uninstall`. It removes the installed package; it does not touch your weights or
the download cache.

### `pull` — fetch model weights

```
veizik pull <model>[@<revision>] [--profile P] [--offline] [--quiet]
```

`pull` fetches a model's weights into the local cache and makes them ready, resolving the model name
against the signed catalogue; it honours `--offline`. `run` and `serve` search the cache it fills
(`$VEIZIK_CACHE/models/*/*@*/`). For a gated model, run `veizik hf login` first.

### `hf` — Hugging Face token

```
veizik hf login | logout | status
```

`login` reads the token from standard input (never from the command line): `printf %s "$HF_TOKEN" |
veizik hf login`. The token is used by `pull` for gated repositories; `status` shows whether one is stored and `logout` removes it.

### `remove` — delete from the download cache

```
veizik remove <model>[@<revision>]
```

Deletes a model's (or one revision's) cached weights from the **download cache**. It never touches the
installed package or weights you supplied yourself.

### `convert` — not functional yet (no converter)

```
veizik convert <source> [-o <file>] [--profile fastest|balanced|quality|smallest|auto]
```

The command exists, but there is no converter yet: it checks the source checkpoint and reports, and
it never writes a converted file. Nothing needs converting: `veizik run` reads a Hugging Face
checkpoint as it is.

### `inspect` — what a model is

```
veizik inspect <model> [--json]
```

Shows what is known about a model: its catalogue status, the context window this runtime supports,
and whether it can run here (`--json` prints the same items for scripts). If the weights are not
where the CLI looks for them, `inspect` reports that the model cannot run because its weights are
missing; it shows the full model information when the runtime and weights are present.

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
- For a Qwen model `bench` runs `veizik run <model>` three times with the synthetic prompt and default
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

`info` shows the `veizik pull` download cache; `clean` removes interrupted download work; `--all` also
removes completed models. It does not touch the installed packages or weights you supplied yourself.

### `config` — settings

```
veizik config show
veizik config set <key> <value>
veizik config unset <key>
veizik config path
```

Keys: `cache.path`, `default.model`, `default.profile`, `offline`, `activation.host`, `license.id`,
`serve.allowed_origins`. `activation.host` (the activation service address) is normally not needed, and
`license.id` is filled in automatically by activation. The settings
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
veizik activate [<model>]                         # approve the printed address and code in a browser
veizik activate --key KEY [--password-stdin]      # browser-free
veizik activate --refresh                         # renew the lease only
```

Activation is **per device**. One approval covers all installed models; naming a model narrows it to
that engine. Activation needs the network.

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
enrolment) is **not available in the shipped build** and is refused (exit 2); `--license` is no longer
accepted. `veizik activate --help` prints this help and exits 2.

Activation ends with one short check generation using `qwen35_0p8b`, so that model's weights must be
on this machine ([`README.md`](README.md) §2, "Model weights"). Without them activation installs the lease, reports that the device is
**not confirmed** (exit 6), and tells you to get the weights and run `veizik activate` again.
Exit `0` activated · `2` usage / bad key, e-mail or code · `5` `--refresh` failed · `6` the service
refused, install failed, or the check generation did not confirm the device · `130` interrupted.

```bash
printf '%s' "$CLI_PASSWORD" | veizik activate --key vzek_… --password-stdin
```

### `devices` — the devices on your licence

```
veizik devices                         # list
veizik devices disable <tag>           # hand a device back; frees its slot
veizik devices enable <tag>            # let a device run again
```

`devices` lists the devices on your licence and switches one on or off by its tag. `veizik device-id`
prints this machine's tag. To turn off a machine you no longer have, use your account page. Needs an
activated device. Exit `0` · `2` · `6`.

### `doctor` — check this installation

```
veizik doctor
```

Reports `root`, `backend`, the activation service address (and where it was configured), the
model catalogue, the integrity of the CLI binary, the lease helper state, and a final `status`. Exit `0`; `6` when no engine is found (set `VEIZIK_ROOT`). It does
**not** check your GPU, driver, weights or lease — use `nvidia-smi` and `veizik status` for those.

### `device-id` — this machine's id

```
veizik device-id
```

Prints this machine's device id. It is the same id the device list on the website shows, so you can
match a machine to its entry (and use it as the tag for `veizik devices enable|disable`).

### `version`

```
veizik version        # prints the CLI version and the backend (CUDA)
```

Also `--version`, `-v`, `-V`. The CLI version (1.4.3) is numbered separately from the package versions
(Qwen `1.1.0`, WAN `1.2.0`).

---

## Environment variables

| variable | effect |
|---|---|
| `VEIZIK_ROOT` | the engine folder the CLI uses; normally not needed (the CLI finds an engine installed with `veizik install`, and the `veizik` command from a manual `install.sh` sets it) |
| `VZ_WEIGHTS` | where to look for model weights (`run`, `chat`, `bench`, `serve`, and the activation check) |
| `VEIZIK_CACHE` | the `veizik pull` cache root, searched by `run` and `serve` |
| `HF_HUB_CACHE`, `HF_HOME` | where the Hugging Face cache lives (searched by `run` and `bench`) |
| `VEIZIK_OUT` | default output folder for `run` and scratch folder for the CLI (else `~/veizik-out`) |
| `Q35_SEAL_ARCH` | only if `nvidia-smi` is unavailable or your GPUs differ: one of `sm80`, `sm86`, `sm89`, `sm90a`, `sm100a`, `sm120a` |
| `VEIZIK_ACTIVATION_KEY` | read by `activate --key -` |
| `VEIZIK_ACTIVATION_PASSWORD` | CLI password source when no password option is given (`--password-stdin` is safer) |
| `VEIZIK_ACTIVATION_EMAIL` | read by `activate --email -` |
| `VEIZIK_ACTIVATION_HOST` | overrides the activation service address (normally not needed) |
| `VEIZIK_LEASE_DAEMON` | set to `0` to use a per-run lease instead of the RAM-only lease helper |
| `XDG_STATE_HOME`, `XDG_CONFIG_HOME` | where activation state and settings are kept |
| `NO_COLOR` | turn off coloured output |

Veizik does not read model credentials from the environment for generation, and generation makes no
network calls; only activation, lease renewal and `pull`/`hf` use the network.

---

## One-screen cheat-sheet

```bash
curl -fsSL https://veizik.com/install.sh | sh   # the veizik command only
veizik install qwen36                           # or: veizik install wan22
veizik version                                  # CLI version + backend
veizik activate                                 # register this device (once; one approval covers all models)
veizik status                                   # activation, expiry
export VZ_WEIGHTS=/data/models                  # folder holding Qwen3.5-0.8B/, Qwen3.5-9B/, …
veizik run qwen35_9b "…" --mode balanced        # generate once; output in ~/veizik-out/<run>/gen.txt
veizik run wan22_t2v_a14b "…" --out $HOME/clip  # video: PNG frames in $HOME/clip/frames/
veizik chat qwen35_2b                           # interactive session in the terminal (/exit leaves)
veizik serve qwen35_2b --weights $VZ_WEIGHTS/Qwen3.5-2B   # OpenAI-compatible server on 127.0.0.1:8000
veizik ps ; veizik stop 8000                    # list and stop resident servers
veizik bench qwen35_9b                          # time this machine
veizik doctor                                   # check the install
```
