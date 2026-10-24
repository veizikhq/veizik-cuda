# veizik-cuda 1.1.0 (Qwen3.5 / Qwen3.6) — Detailed Usage Guide (CLI 1.4.3)

Goes beyond the command reference ([`CLI_USAGE.md`](CLI_USAGE.md)): how the run modes actually
behave, serving over HTTP, long-context prompts, sampling, performance, and troubleshooting. Every
behavior below is what the shipped package does, not a roadmap; where something is not in this
release the text says so.

---

## 1. Run modes

| mode | command | use it for | streaming | concurrency |
|---|---|---|---|---|
| one-shot | `veizik run <model> "<prompt>"` | scripts, single generations | no — the output is written to `gen.txt` when the run finishes | one generation per process |
| interactive | `veizik chat <model>` | talking to a model in the terminal: type a message, read the text reply, repeat (each message is answered on its own; no history is kept between messages) | — | — |
| HTTP server | `veizik serve <model>` | chat and text completions for applications and OpenAI-compatible clients (`POST /v1/chat/completions`) | **yes** — server-sent events (§2) | batched across a fixed number of slots (§2) |

All three need `veizik activate` and the model weights before they generate. The same commands and the
same `run` flag vocabulary serve the WAN video models; their guide is [`wan/README.md`](wan/README.md).

Each `run` loads the model, generates and exits, so model load time is paid on every invocation. Use
`serve` to keep the model resident.

**Profiles.** The user-selectable performance profile is `--mode`, and only on `run`:
`quality`, `balanced` (default), `fast`, `ultrafast`, `low-memory` (§5). `serve` takes no `--mode`; it
always runs the `balanced` configuration. `bench` runs `balanced`. An unknown mode is an error
(exit 2), never a silent substitution.

**Output.** `veizik run` writes its output to `gen.txt` in `--out`; for text use `veizik chat` or `veizik serve`.

**Chatting in the terminal.** `veizik chat <model>` opens an interactive prompt: type a message, read
the model's text reply, repeat; `/help` lists the in-session commands and `/exit` leaves. Each message
is answered on its own (no history is kept between messages). Set `VZ_WEIGHTS` or keep the
checkpoint in the Hugging Face cache first, as for `run` (`chat` has no `--weights` option). For
programs, use the HTTP server below.

**Prompt format.** `run` and `POST /v1/completions` use the prompt exactly as written. For an
instruct-style answer from `run`, wrap the text in the model's chat format:

```bash
P=$(printf '<|im_start|>user\nExplain attention in two sentences.<|im_end|>\n<|im_start|>assistant')
veizik run qwen35_4b "$P" --tokens 96 --out ./out
```

`--tokens N` (or `--max-tokens N`) sets the generation length; add `--ignore-eos` (no value) to emit
exactly N tokens instead of stopping at the end-of-turn token. A text prompt is used as written, so with
a chat-formatted prompt trim the output at `<|im_end|>`. The chat endpoint of `serve` applies
the chat template for you and stops at end-of-sequence. Image and video runs (§1a) apply the chat
template themselves and end at the end-of-turn token.

---

## 1a. Image and video input (Qwen3.6-35B-A3B only)

New in 1.1.0. On Qwen3.6-35B-A3B, `veizik run` can look at one image or one short video together with a
text prompt. The other four models take text only, and `veizik chat` and `veizik serve` take text only
(`serve` answers an image or other non-text message part with 400 `unsupported_content_part`). The
flags are accepted for `qwen36_35b_a3b` only; any other model refuses them with `<flag> does not apply to this model.`

```bash
# one image; photo.png stands for your own PNG or JPEG file
veizik run qwen36_35b_a3b "What is in this picture?" --image photo.png

# one video: a folder of PNG or JPEG frames, all the same size; file-name order is time order
veizik run qwen36_35b_a3b "$(cat question.txt)" --video ./frames --video-fps 2
```

| option | default | meaning |
|---|---|---|
| `--image FILE` | — | a PNG or JPEG file; exactly one image per run |
| `--image-max-pixels N` | 1,048,576 | upper bound on the image's pixel count after resizing (65,536 – 16,777,216); a larger image is scaled down to fit. More pixels keep more detail and use more memory and time |
| `--video DIR` | — | a folder of 2 to 256 PNG or JPEG frames, all the same size, in file-name order; exactly one video per run |
| `--video-fps X` | 2 | the frame rate of the frames in the folder (0.001 – 1000); it sets the time stamps the model sees between frames |
| `--video-max-pixels N` | 262,144 | upper bound on every frame's pixel count after resizing (65,536 – 16,777,216); more pixels keep more detail and use more memory and context |

Rules:

- One image **or** one video per run, never both, and always with a text prompt.
- The chat template is applied for you, and the answer ends at the end-of-turn token.
- To keep frame names in time order, number them with leading zeros (`0001.png`, `0002.png`, …).
- The image and video stage ships GPU code for `sm_86`, `sm_89` and `sm_120a`. On a GPU the image and video stage does not support, the run is refused cleanly with code 50 (`the image stage refused this request (status 50)`) before any image or video work.
- Images and frames add to memory use on top of the model's ≈ 21.7 GiB resident text footprint. No
  memory or speed figure is published for image or video input in this release.

| exit | meaning for image / video runs |
|---|---|
| `2` | `--image` or `--video` on a model that does not take it; more than one image or video; `--image` with `--video`; no text prompt; an unsupported or damaged file; frames of different sizes, or fewer than 2 / more than 256 frames; or over the size or aspect-ratio budget |
| `3` | the image file or the video frames folder is missing or unreadable |

---

## 2. Serving over HTTP (`serve`) — in depth

```bash
export VZ_WEIGHTS=/data/models/Qwen3.5-2B       # the checkpoint folder itself (tokenizer.json + tokenizer_config.json inside)
veizik serve qwen35_2b --port 8000              # foreground; Ctrl-C stops it

# in another terminal: wait until the model is loaded
until curl -sf http://127.0.0.1:8000/readyz >/dev/null; do sleep 2; done
```

The engine loads the model once and answers HTTP itself on `127.0.0.1:<port>`; `veizik serve` is the
launcher that supplies the device lease and waits for the port. Send traffic only after the engine
reports ready: `GET /health` answers 503 and `GET /readyz` is not ready until loading has finished
(a 35B-A3B load reads about 70 GB of weights and depends on your disk). One server hosts one model;
run another `serve` on another port for a second model.

### Endpoints

| method | path | returns |
|---|---|---|
| `GET` | `/v1/models` | the one model id this server answers to (the model key, for example `qwen35_2b`) |
| `POST` | `/v1/chat/completions` | a chat completion — supported for all five models (the shipped signed model catalogue declares chat capability for each); the server applies the model's chat template; `"stream": true` returns server-sent events |
| `POST` | `/v1/completions` | a text completion; the prompt is used as written |
| `GET` | `/health` | readable status JSON: 200 when serving (`ok` or `busy`), 503 while starting or unavailable |
| `GET` | `/healthz` (`/livez`) | liveness — failure means restart |
| `GET` | `/readyz` (`/ready`) | readiness — failure means take out of rotation, not restart |
| `GET` | `/metrics` | Prometheus text; served on a loopback bind, otherwise only with a key |
| `POST` | `/shutdown`, `/restart` | answer 403 on this server — stop it with Ctrl-C |

### Call it

```bash
# chat completion
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"qwen35_2b","messages":[{"role":"user","content":"Say hello in Korean."}],"max_tokens":64}'

# text completion
curl -s http://127.0.0.1:8000/v1/completions \
  -H 'content-type: application/json' \
  -d '{"model":"qwen35_2b","prompt":"The capital of France is","max_tokens":24}'

# streaming (server-sent events); -N turns off curl's buffering
curl -sN http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"qwen35_2b","messages":[{"role":"user","content":"Count to five."}],"max_tokens":48,
       "stream":true,"stream_options":{"include_usage":true}}'
```

```python
# any OpenAI client works — point base_url at the local server
from openai import OpenAI
client = OpenAI(base_url="http://127.0.0.1:8000/v1", api_key="not-used")
r = client.chat.completions.create(model="qwen35_2b", max_tokens=64,
                                   messages=[{"role": "user", "content": "Say hello in Korean."}])
print(r.choices[0].message.content, r.usage.total_tokens)
for ev in client.chat.completions.create(model="qwen35_2b", max_tokens=48, stream=True,
                                         messages=[{"role": "user", "content": "Count to five."}]):
    print(ev.choices[0].delta.content or "", end="")
```

Response shapes (field values are illustrative):

```json
{"id":"chatcmpl-7","object":"chat.completion","created":1790000000,"model":"qwen35_2b",
 "choices":[{"index":0,"message":{"role":"assistant","content":"안녕하세요."},"finish_reason":"stop"}],
 "usage":{"prompt_tokens":14,"completion_tokens":6,"total_tokens":20}}
```

`/v1/completions` returns `"object":"text_completion"` with `"text"` and `"logprobs":null` in each
choice. `finish_reason` is `"stop"` (end-of-sequence or a `stop` string) or `"length"` (`max_tokens`
reached). `completion_tokens` counts tokens actually emitted. `GET /v1/models` returns
`{"object":"list","data":[{"id":"qwen35_2b","object":"model","created":…,"owned_by":"veizik"}]}`.

A stream is a sequence of `data: {…}` events with `Content-Type: text/event-stream`: a first chunk
whose `delta` carries `"role":"assistant"`, content deltas, a chunk with an empty `delta` and the
`finish_reason`, an extra chunk with `usage` only when `stream_options.include_usage` is true, and
finally `data: [DONE]`. Deltas are valid UTF-8. If the engine fails after the first byte, the error
arrives as an event inside the stream and no `[DONE]` follows.

### Behavior you must design around

- **Model id.** `model` is required and must equal the id from `GET /v1/models` (the model key). A
  different id answers 404 `model_not_found`.
- **Context window.** In the validated configuration each request has a 4,096-token window: prompt
  plus `max_tokens` must fit, otherwise 400 `context_length_exceeded` (naming `messages` or
  `max_tokens`). Prompts longer than the chunk size are prefilled in chunks (a 1,103-token prompt
  was served in validation). See §3.
- **`max_tokens` budget.** When omitted the server uses its own default (256 tokens in the engine's
  configuration); `max_completion_tokens` is accepted as a synonym on the chat endpoint, and sending
  both with different values is a 400. Qwen3.5/3.6 may produce a reasoning section before the
  answer, and every generated token counts: a one-sentence answer from Qwen3.6-35B-A3B used 164
  generated tokens in validation. `enable_thinking` (and `chat_template_kwargs.enable_thinking`) is
  accepted and handed to the chat template.
- **Concurrency.** Requests are batched across generation slots: 8 for the dense models and 24 for
  Qwen3.6-35B-A3B in the validated configuration. In validation 8 concurrent requests on a dense
  model and 4 on 35B-A3B all returned 200 with correct answers. Past capacity a request waits or is
  refused with 503 `server_overloaded` (with a `Retry-After` header) or 429 `rate_limit_exceeded`;
  retry with backoff. HTTP/1.1 keep-alive is supported. Every response carries an `X-Request-Id`
  header you can quote in a report.
- **Bind scope.** The server is **loopback-only**: it listens on `127.0.0.1`, and `--host` accepts
  only `127.0.0.1` or `localhost` — any other address (for example `0.0.0.0`) is refused with exit 2.
  It is not reachable from other machines. To serve other machines, put a **reverse proxy** on the
  same host in front of it: the proxy terminates TLS on the external address and forwards to
  `127.0.0.1:<port>`. Keep `--require-auth` on behind the proxy (the proxy either sends the key
  itself or passes the client's `Authorization` header through), and let only the proxy listen on
  an external address. Streaming needs a proxy that does not buffer server-sent events (for nginx,
  `proxy_buffering off`).
- **Authentication.** Without `--require-auth` the CUDA server has **no authentication**: it is open
  to every local process on the machine. Turn it on with a key:

  ```bash
  ( umask 077; head -c 24 /dev/urandom | od -An -tx1 | tr -d ' \n' > ~/.veizik-serve.key )
  veizik serve qwen35_2b --weights /data/models/Qwen3.5-2B --require-auth --keyfile ~/.veizik-serve.key

  curl -s http://127.0.0.1:8000/v1/models                                   # 401 invalid_api_key
  curl -s http://127.0.0.1:8000/v1/models -H "Authorization: Bearer $(cat ~/.veizik-serve.key)"   # 200
  ```

  With the key on, a request with no key or a wrong key answers **401** with error code
  `invalid_api_key` and a `WWW-Authenticate: Bearer` header; the right key is served normally. It
  covers `/v1/chat/completions`, `/v1/completions` and `/v1/models`. `/health`, `/healthz` and
  `/readyz` need no key (they are probe endpoints), and `/metrics` requires it. The key is 8–256
  printable ASCII characters with no spaces, one shared key per server process (not per-user keys).
  **Use `--keyfile`** (first line of the file): `--api-key K` works too but leaves the key on the
  `veizik serve` command line, visible to every local user in `ps`. The CLI passes the key to the
  engine through its environment (`SV_API_KEY`), not on the engine's command line, and never prints
  it. In an OpenAI client, set `api_key` to the key. A usage ledger, tenant quotas and a per-user key
  store are **not** part of the CUDA server.
- **Speed over HTTP.** The server batches requests and does not use the speculative decoding that the
  one-shot `balanced` figures include, so per-request speed over HTTP is not the number in the
  benchmark board. Server throughput is not published for this release.
- **Unsupported fields are rejected, not ignored.**

| you send | answer |
|---|---|
| no `model`, or neither `messages` nor `prompt` | 400 `missing_required_parameter` |
| body that is not JSON / is empty | 400 `invalid_json` / 400 `empty_body` |
| `Content-Type` other than `application/json` | 415 `unsupported_media_type` |
| a body without `Content-Length` | 411 `length_required` |
| body or prompt over the size limits | 413 `request_too_large` / `prompt_too_large` |
| image or other non-text message parts | 400 `unsupported_content_part` |
| `tools`, `tool_choice`, `functions`, `function_call`, `response_format`, `logprobs`, `top_logprobs`, `logit_bias`, `presence_penalty`, `frequency_penalty`, `best_of`, `suffix`, `echo`, `store`, `modalities`, `audio`, `prediction`, `reasoning_effort`, `verbosity`, `web_search_options` set to anything but an "off" value (`null`, `false`, `0`, `[]`, `{}`) | 400 `unsupported_parameter` naming the field |
| `n` greater than 1 | 400 |
| a field name that is not an OpenAI request field | 400 `unknown_parameter` |
| sampling fields the server cannot apply (§4) | 400 `unsupported_parameter` |
| `stream_options` without `"stream": true` | 400 `invalid_value` |
| values out of range | 400 `invalid_value` |
| prompt + `max_tokens` over the window | 400 `context_length_exceeded` |
| a chat template the server does not know | 501 `chat_template_unsupported` |
| a request that runs past its deadline (120 s default) / stalls while sending | 504 `timeout` / 408 `request_timeout` |
| the server is stopping | 503 `server_draining` |

  Accepted and ignored (they change nothing in the answer): `user`, `metadata`, `service_tier`,
  `safety_identifier`, `prompt_cache_key`, `prompt_cache_retention`. Error bodies follow the OpenAI
  shape `{"error":{"message","type","param","code"}}`.

- **Omitted from responses.** There are no log-probabilities (`logprobs` is `null` on the
  completions endpoint and absent on the chat endpoint), no `system_fingerprint`, and only one
  choice is returned.

### Managing the server

`veizik ps` lists the resident servers running on this machine, and `veizik stop <port>` or
`veizik stop all` stops them. A server run in a terminal can also be stopped with Ctrl-C: the signal
reaches the engine, which drains in-flight requests and exits.

Exit codes of `veizik serve`: `2` usage, invalid model name or a bad/misplaced API-key option, `3` weights not found, `6` no
launcher or not a text package, `4` integrity or GPU modules, `70`/`74` activation; otherwise the
engine's code (`0` after a clean stop).

### Memory when serving

Weights and the batched KV cache are resident together. As recorded in validation: Qwen3.5-0.8B
about 3.4 GB in use at ready; Qwen3.6-35B-A3B 27.1 GB in use of 32.6 GB at ready on an RTX 5090
(24 slots × 4,096-token window). Qwen3.6-35B-A3B was not validated for serving on 24 GB cards.

---

## 3. Long context

- **Server:** a 4,096-token window per request in the validated configuration (prompt plus generated
  tokens). The longest prompt served in validation was 1,103 tokens, prefilled in chunks.
- **One-shot:** `--tokens` accepts 1–4096 generated tokens. Measured one-shot runs used a 21-token
  prompt and generated 128 or 1,024 tokens (board rows in [`bench/REPRODUCIBILITY.md`](bench/REPRODUCIBILITY.md));
  one-shot runs with long prompts were not measured for this release.
- **Prefill vs decode.** A long prompt is processed first (prefill) and generation then proceeds one
  token at a time (decode). The engine prints prompt and decode timing separately at the end of a
  run, so you can see where time goes on your own prompt. Prefill throughput is not published for
  this release (the measured prompt pass is only 21 tokens and is latency-bound).
- **Memory grows with context** (the KV cache scales with positions) on top of the resident weights.
  If a long-prompt run is tight, use a smaller model, `--mode low-memory`, or a shorter prompt.
- Put long prompts in a file and pass them as `"$(cat question.txt)"`. For the server, keep prompt plus
  `max_tokens` inside the window or split the document.

---

## 4. Sampling

- **Default is greedy** and deterministic: the same input, mode and package give the same output
  (identical output hashes on repeated runs in every completed measured cell).
- `veizik run` accepts `--temperature X` (0–2), `--top-p X` (0–1), `--top-k N` (0–1000) and
  `--seed N`. The sampler is **experimental**: it is outside the guarantees of this release. On
  Qwen3.6-35B-A3B, requesting sampling turns off speculative decoding for that run and the launcher
  says so.
- `veizik chat` has no sampling options. `veizik serve` has no sampling flags. In requests, the sampling
  fields `temperature`, `top_p`, `top_k`, `min_p`, `repetition_penalty` and `seed` are either applied
  or rejected with 400 `unsupported_parameter` — never silently ignored. Per-request sampling is not
  part of the verified contract of this release; greedy decoding is.

```bash
veizik run qwen35_9b "Give me a product tagline." --temperature 0.8 --top-p 0.9 --seed 7   # experimental
veizik run qwen35_9b "Give me a product tagline."                                          # greedy
```

---

## 5. Performance — what you can tune

The one speed / quality / memory control is `--mode` on `run`:

| mode | what it is for | measured here |
|---|---|---|
| `quality` | closest to the original checkpoint; most memory, slowest | 7–21 % lower decode tok/s than `balanced` on the dense models; Qwen3.6-35B-A3B in this mode did not complete on a 32 GB RTX 5090 (the engine exited 2 after loading), and the launcher falls back to `balanced` on GPUs under about 26 GB with a message |
| `balanced` *(default)* | the configuration every published speed figure is measured with | the board in [`bench/REPRODUCIBILITY.md`](bench/REPRODUCIBILITY.md) |
| `fast` | a speed preset | no change on the four dense models (same decode tok/s and memory as `balanced`, within run-to-run noise); +21 % decode tok/s on Qwen3.6-35B-A3B at the same memory (544.7 vs 449.9 tok/s on an RTX 5090) |
| `ultrafast` | the quickest preset; same trade-off as `fast` | not measured separately in this release |
| `low-memory` | smallest footprint, lowest quality | not measured in this release |

What you can do:

- **Pick the model.** Model size is the biggest lever. All four dense models fit one 24 GB card;
  Qwen3.6-35B-A3B needs about 22 GiB resident in `balanced`/`fast` and was measured on a 32 GB card.
- **Measure your machine.** `veizik bench <model>` times three end-to-end runs (median, model load
  included). For decode tok/s use the per-run timing lines the engine prints; the exact method is in
  [`bench/REPRODUCIBILITY.md`](bench/REPRODUCIBILITY.md). Run on an otherwise idle GPU, with the same
  power limit you will deploy with, and repeat at least three times.
- **Keep the weights on fast local storage.** Every `run` and every server start reads them; a slow
  network or spinning disk dominates load time for the 35B model.
- **Keep the model resident** with `serve` instead of repeated `run` cold starts.
- **Close other GPU programs** before a large model.

---

## 6. Troubleshooting

| symptom | meaning | fix |
|---|---|---|
| `no Veizik NVIDIA engine here (<root>)` (exit 6) | the CLI cannot find the engine folder | `export VEIZIK_ROOT=<engine folder veizik install prints>` (after a manual install: `<install>/veizik-qwen-cuda-0.1.0-rc1-linux-x86_64-sm86`) |
| `activation … NOT confirmed` / "model weights are not on this machine yet" (exit 6) | the lease installed but the check generation could not run | get the `Qwen3.5-0.8B` checkpoint, set `VZ_WEIGHTS`, run `veizik activate` again |
| exit `70` `VZ_ACTIVATION_REQUIRED` | no key, no lease, or the lease expired | `veizik activate` (or `veizik activate --refresh`) |
| exit `74` `VZ_ENTITLEMENT_REFUSED` | a lease is present but was not issued for this package on this device | `veizik activate --reapprove`; make sure the installed engine folder was not renamed |
| exit `3`, "weights for `<model>` … not found. Looked in:" | no complete checkpoint of that model | download the full snapshot (config, tokenizer, every weight file) and use `VZ_WEIGHTS` or the Hugging Face cache (`--weights` on `serve`), or `veizik pull <model>` |
| exit `3` from `serve`: "could not find the weights … tokenizer.json and tokenizer_config.json" | `serve` needs the checkpoint folder itself, with both tokenizer files | pass `--weights <checkpoint folder>` or set `VZ_WEIGHTS` to that folder (not its parent) |
| `the checkpoint has no tokenizer.json` (exit 3) | a text prompt needs the tokenizer file | download the complete snapshot |
| exit `4` `VZ_PTX_BOOT_FAIL` | the engine failed its integrity check, or its GPU modules did not open | reinstall from the tarball after verifying its SHA-256; never edit the installed folder |
| exit `2` "cannot read the GPU compute capability" / "GPUs with different compute capabilities" / "unusable compute capability" | `nvidia-smi` is missing, or the GPUs differ | `export Q35_SEAL_ARCH=sm86` (or `sm80`, `sm89`, `sm90a`, `sm100a`, `sm120a`) to match your GPU |
| "compute capability N.M has no kernel set in this bundle" | your GPU architecture is not in this package | supported: 8.0, 8.6, 8.9, 9.0, 10.0, 12.0 |
| exit `2` "unknown option … for run." | a misspelt or unsupported option | check [`CLI_USAGE.md`](CLI_USAGE.md); options are exact |
| exit `2` "`<flag>` does not apply to this model." | the flag is not in this engine's accepted set | use only the flags listed for the model in [`CLI_USAGE.md`](CLI_USAGE.md) (`run`) |
| exit `2` "`--out` takes an absolute directory" / "`--out` must be outside the bundle" | `--out` is relative, or inside the engine folder | give an absolute folder outside the engine folder (the default `~/veizik-out` is fine) |
| `quality … does not fit this N MiB GPU; using balanced` | 35B-A3B `quality` needs about 26 GB or more | accept `balanced`, or use a larger card |
| CUDA out-of-memory | the model, mode and context do not fit | use a smaller model or `--mode low-memory`; close other GPU programs |
| `run` / `serve` exits `1` after the engine finished | the engine could not confirm the configuration it ran in; the result is not what you asked for | re-run; report it if it repeats |
| exit `2` on an `--image` / `--video` run | wrong model, more than one input, no text prompt, or an unusable file or frame set | see §1a |
| "the image stage refused this request (status 50)" | the GPU has no image / video stage code (supported: `sm_86`, `sm_89`, `sm_120a`) | use a supported GPU, or text input |
| `veizik pull` stops on a gated model | the model needs a Hugging Face token | `printf %s "$HF_TOKEN" \| veizik hf login`, then pull again; or download the snapshot yourself and use `VZ_WEIGHTS` |
| `veizik inspect` reports the model's weights as missing | the weights are not where the CLI looks | set `VZ_WEIGHTS`, or `veizik pull <model>` |
| `veizik models` shows `incomplete (no weights)` | a per-model status label: the weights are external to the install | ignore it; check with `veizik run …` |
| you want a conversation, not a one-shot answer | `run` is one-shot | use `veizik chat <model>` in the terminal, or `veizik serve` and `POST /v1/chat/completions` (§2) from a program |
| `serve` printed "is loading …", or requests fail right after start | the model is still loading | wait for `GET /readyz` to return 200 |
| HTTP 404 `model_not_found` | `model` is not the server's id | use the id from `GET /v1/models` |
| HTTP 400 `context_length_exceeded` | prompt plus `max_tokens` exceed the window | shorten the prompt or lower `max_tokens` |
| HTTP 400 `unsupported_parameter` | a field this server does not implement, or a sampling value it cannot apply | remove the field (§2 table) |
| HTTP 401 `invalid_api_key` | the server was started with `--require-auth` and the request has no key or a wrong one | send `Authorization: Bearer <key>` (the key in the file you passed to `--keyfile`) |
| `serve` exits 2: "`--require-auth` needs `--api-key <key>` or `--keyfile <path>`" / "`--api-key`/`--keyfile` requires `--require-auth`" | the key option and `--require-auth` must be given together | pass both, with exactly one key source |
| `serve` exits 2: "`--api-key`/`--keyfile` must be 8..256 printable ASCII bytes, no spaces" / "`--keyfile` could not be read, or is empty" | the key is too short, too long, has a space or non-ASCII byte, or the file is unreadable | use 8–256 printable characters without spaces; the key is the first line of the file |
| `serve --host 0.0.0.0` exits 2 | the CUDA server is loopback-only | keep `--host 127.0.0.1` and put a TLS reverse proxy in front |
| `veizik ps` does not list your server | no resident server is running on this machine, or it already exited | start it again with `veizik serve`; `veizik stop <port>` stops one |
| HTTP 503 `server_overloaded` / 429 `rate_limit_exceeded` | no free slot or a concurrency limit | retry with backoff |
| `veizik update` or `veizik convert` does nothing useful | both exist as commands but are not functional yet | reinstall with `veizik install <model>`; no conversion is needed, `run` reads a Hugging Face checkpoint as it is |
| anything under WSL | the sealed engine does not run on WSL | use a native Linux host |
| `install: install path has an unsafe character` | the destination path has characters outside letters, digits and `/ . _ - ~ + @ :` and space | use a plain path |

When reporting an issue, include `veizik version`, `veizik doctor`, `veizik status`, your GPU model
and driver (`nvidia-smi`), the exact command, and the `veizik-run:` lines printed before the failure.
Never include your device key files, activation key or CLI password. Support: support@veizik.com.

---

## 7. What Veizik does not do

- It does not change the licence of the checkpoint you supply (`veizik pull` fetches a publisher's
  weights under that publisher's licence).
- Generation makes no network calls. Only activation, lease renewal (`run` and `serve` renew a lease
  that is within 3 days of expiring), and `pull`/`hf` use the network.
- It does not upload prompts, outputs or telemetry.

Not in this release: LoRA adapters; image or video input on the Qwen3.5 models or through `chat` /
`serve`; audio input; a weight converter (`veizik convert` and `veizik update` exist but are not
functional yet); tool or function calling, `logprobs`, structured output and embeddings over HTTP;
per-user API keys, an in-server usage ledger and tenant quotas on the CUDA server; a non-loopback
bind through the CLI; published server throughput.
