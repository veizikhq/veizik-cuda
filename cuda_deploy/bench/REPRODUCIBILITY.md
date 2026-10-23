# veizik-cuda (Qwen3.5 / Qwen3.6) — Benchmark Data & Reproducibility

Every figure on the Veizik CUDA Qwen board is **Veizik's own measured figure**, and every one of
them can be reproduced on your own GPU with the committed kit here. This document ties the three
layers together: the measured data, the harness that produced it, and the step-by-step reproduction.

> **Board policy.** The board shows Veizik's own absolute figures only (decode tokens/s, resident
> memory). It carries no comparison with other products, and nothing in this kit drives or names
> another engine. A row without its GPU, mode, operating point and run count is not a result.

---

## 1. The three layers (all in git)

| layer | location | what it is |
|---|---|---|
| **Measured result data** | [`results/`](results/) | per-GPU `*_rows.json` (board rows with per-run values and spread) and `*_bench.txt` (the neutral per-run measurement lines each row was computed from) |
| **Reproduction kit** | [`repro_kit/`](repro_kit/) | the pinned prompt + SHA manifest + the grid and extraction scripts |
| **This guide** | `REPRODUCIBILITY.md` | how to go from a clean GPU host to your own comparable numbers |

`*_bench.txt` carries one line per run (exit code, generated tokens, prompt tokens and milliseconds,
decode steps and milliseconds, tokens/s, memory, output hash); `*_rows.json` is derived from those
lines by `repro_kit/run/extract_rows.py`. Engine log lines that carry no measurement are not published.

---

## 2. What is measured

| axis | definition | published as |
|---|---|---|
| `decode` | the engine's own figure: decode steps divided by decode time. A run of N generated tokens times N−1 steps (the first token comes from the prompt pass), so a 128-token run times 127 steps | tok/s |
| `resident_memory` | device memory in use after the weights and the decode graph are loaded (GiB = 2^30 bytes, the `nvidia-smi` MiB figure / 1024). Not the transient peak during decode | GiB |

Not published for this release: **prefill throughput** (the measured prompt pass covers only 21
tokens and is latency-bound), **server (HTTP) throughput**, long-prompt runs, and `ultrafast` and
`low-memory` modes.

**Operating points.**

- *Functional cell* — prompt `repro_kit/prompts/fact_chatml.txt` (a ChatML user turn; the engine
  reports **21 prompt tokens**), `--seed 42`, **128 generated tokens**, modes `balanced`, `quality`,
  `fast`, **2 runs** per cell (`r1`, `r2`). The row value is the median of the completed runs (for 2
  runs, their mean); `per_run` lists both.
- *1,024-token cell* — the same prompt, `balanced`, **1,024 generated tokens**, **1 run**.
- Greedy decoding throughout. `veizik run` uses speculative decoding where the mode enables it; the
  HTTP server does not, so these figures are not server figures.

**Models** (Hugging Face repositories; the measurement run downloaded the default-branch snapshot on
2026-10-21 and did not pin a revision — when you reproduce, record the snapshot hash from the
folder name in your Hugging Face cache):

| model key | repository |
|---|---|
| `qwen35_0p8b` | `Qwen/Qwen3.5-0.8B` |
| `qwen35_2b` | `Qwen/Qwen3.5-2B` |
| `qwen35_4b` | `Qwen/Qwen3.5-4B` |
| `qwen35_9b` | `Qwen/Qwen3.5-9B` |
| `qwen36_35b_a3b` | `Qwen/Qwen3.6-35B-A3B` |

---

## 3. Provenance — which build, which GPUs

- Measured **2026-10-21** with `veizik-cuda 1.0.0` on the previous build of this package (the
  LLM-only 1.0.0 build), CLI `veizik run`, on single-GPU cloud hosts, native Linux, driver 595.91.07.
- **These are previous-version rows.** The shipped package is now `veizik-qwen-cuda-1.1.0`
  (`43586587…`). The rows were measured on 1.0.0 builds of this package, with text input, and were
  not re-measured on 1.1.0; their output hashes were not compared against the table in §4 on 1.1.0.
  The `prov` label in the data files names the 1.0.0 tarball that was current when the rows were
  labelled; the data files are kept as recorded. No figure is published for image or video input.
  Re-run the kit on the shipped bytes to produce same-build rows.
- Power and load: the hosts were dedicated to the run and the GPUs ran at their default board power
  (the limit was not recorded). **No quiet-gate was applied** — no host-load check is recorded for
  these runs, so they carry the grade "N = 2, dedicated host". Treat the figures as indicative to
  about ±2 %, which is the largest run-to-run spread observed.

| GPU | arch | memory | driver | rows file |
|---|---|---|---|---|
| RTX 3090 | `sm_86` | 24 GB | 595.91.07 | [`results/RTX3090_rows.json`](results/RTX3090_rows.json) |
| RTX 4090 | `sm_89` | 24 GB | 595.91.07 | [`results/RTX4090_rows.json`](results/RTX4090_rows.json) |
| RTX 5090 | `sm_120a` | 32 GB | 595.91.07 | [`results/RTX5090_rows.json`](results/RTX5090_rows.json) |

`sm_80`, `sm_90a` and `sm_100a` (A100, H100, B200) have no rows: that GPU code is included but was
not measured. Qwen3.6-35B-A3B was measured on the RTX 5090 only.

---

## 4. The board

### Decode, tokens/s — `balanced` (median of 2 runs, 128 generated tokens)

| model | RTX 3090 | RTX 4090 | RTX 5090 |
|---|---|---|---|
| Qwen3.5-0.8B | 940 | 1318 | 1529 |
| Qwen3.5-2B | 583 | 887 | 1138 |
| Qwen3.5-4B | 369 | 532 | 772 |
| Qwen3.5-9B | 190 | 347 | 499 |
| Qwen3.6-35B-A3B | — | — | 450 |

### Decode, tokens/s — `quality`

| model | RTX 3090 | RTX 4090 | RTX 5090 |
|---|---|---|---|
| Qwen3.5-0.8B | 861 | 1156 | 1438 |
| Qwen3.5-2B | 539 | 741 | 1041 |
| Qwen3.5-4B | 344 | 442 | 670 |
| Qwen3.5-9B | 174 | 273 | 423 |
| Qwen3.6-35B-A3B | — | — | not completed |

Qwen3.6-35B-A3B `quality` did not complete on the 32 GB RTX 5090: the engine exited with code 2
(it refuses the configuration) after loading, with 24.4 GiB resident. The row is in the data file with
`status: not_completed`; no number is published for it.

### Decode, tokens/s — `fast`

| model | RTX 3090 | RTX 4090 | RTX 5090 |
|---|---|---|---|
| Qwen3.5-0.8B | 943 | 1316 | 1531 |
| Qwen3.5-2B | 578 | 895 | 1137 |
| Qwen3.5-4B | 368 | 535 | 771 |
| Qwen3.5-9B | 190 | 347 | 498 |
| Qwen3.6-35B-A3B | — | — | 545 |

On the four dense models `fast` runs the same weights configuration as `balanced`; the two columns
differ only by run-to-run noise.

### Decode, tokens/s — `balanced`, 1,024 generated tokens (1 run)

| model | RTX 3090 | RTX 4090 | RTX 5090 |
|---|---|---|---|
| Qwen3.5-0.8B | 1038 | 1439 | 1676 |
| Qwen3.5-2B | 560 | 869 | 1107 |
| Qwen3.5-4B | 390 | 568 | 822 |
| Qwen3.5-9B | 166 | 303 | 435 |
| Qwen3.6-35B-A3B | — | — | 450 |

### Resident memory, GiB — after weights and decode graph are loaded

| model | `balanced` / `fast` (3090 · 4090 · 5090) | `quality` (3090 · 4090 · 5090) |
|---|---|---|
| Qwen3.5-0.8B | 2.27 · 2.40 · 2.51 | 2.42 · 2.55 · 2.66 |
| Qwen3.5-2B | 3.48 · 3.61 · 3.72 | 3.80 · 3.93 · 4.03 |
| Qwen3.5-4B | 5.50 · 5.62 · 5.73 | 6.27 · 6.40 · 6.50 |
| Qwen3.5-9B | 8.44 · 8.57 · 8.67 | 9.82 · 9.95 · 10.05 |
| Qwen3.6-35B-A3B | — · — · 21.67 (`fast` 21.74) | — |

The small difference between cards is the per-GPU runtime overhead. Weights are held in a
memory-efficient format once loaded, and the figure also includes the runtime's own buffers.
`quality` mode uses more resident memory than `balanced` on every model that completed (table above),
and `fast` uses the same memory as `balanced` on the dense models.

### Expected output hash (arch-invariant)

For the committed prompt, `--seed 42`, greedy, 128 tokens, the hash of `gen.txt`
(`sha256sum gen.txt | cut -c1-16`) is identical on all three GPUs for every cell:

| model | `balanced` / `fast` | `quality` |
|---|---|---|
| Qwen3.5-0.8B | `df246a37df059ac9` | `2b9d795930ba1a9d` |
| Qwen3.5-2B | `71ad95be1e60c7d7` | `d74e5d0ad608e112` |
| Qwen3.5-4B | `e6d9b10dd6d5c1c3` | `e6d9b10dd6d5c1c3` |
| Qwen3.5-9B | `3c161a511a1e1f19` | `54ef8510a93c9963` |
| Qwen3.6-35B-A3B | `8fc47b4e703027e2` | — |

These hashes depend on the checkpoint snapshot as well as the package; a different snapshot of the
same repository can give a different hash.

---

## 5. Row schema and grade

Each entry of a `*_rows.json` file is one row with the fleet-common columns:

| column | meaning |
|---|---|
| `model` | model key (`qwen35_9b`) |
| `arch` | CUDA SASS architecture (`sm_89`) |
| `gpu` | card (`RTX 4090`) |
| `power` | measurement power condition (`default board power (not recorded)`) |
| `axis` | `decode` or `resident_memory` |
| `value` | the measured figure (`null` when the cell did not complete) |
| `unit` | `tok/s` or `GiB` |
| `measured_at` | ISO date and the package build measured on |
| `prov` | provenance and grade label |

plus: `mode`, `driver`, `status` (`ok` / `not_completed`), `runs`, `per_run`, `spread_pct`
(max − min over the median), `gen_tokens`, `timed_decode_steps`, `prompt_tokens`, `deterministic`
(identical output hash across runs), `gen_sha`, and for memory rows `device_total_gib`.

**Grade of a published row:** `runs` stated (here 2, or 1 for the 1,024-token rows); fixed generated
token count stated; output hash stated; engine build and date stated; no projected numbers — every
value was measured on the GPU named in the row. Rows measured on a build other than the shipped bytes
carry the *previous-version* label.

---

## 6. Reproduce it on your GPU

Prerequisites: a Linux x86-64 host with an NVIDIA GPU of compute capability 8.0+, the package
installed and activated ([`../README.md`](../README.md) §2–3), the checkpoints for the models you
want in one folder, and Python 3 for the extraction step only.

```bash
cd cuda_deploy/bench/repro_kit

# 0. integrity: the grid refuses to run if the prompt file differs
( cd prompts && sha256sum -c ../SHA256SUMS )                  # → fact_chatml.txt: OK

# 1. run the grid through the installed CLI (two runs per cell + one 1,024-token run per model)
#    VZ_WEIGHTS_ROOT holds Qwen3.5-0.8B/, Qwen3.5-2B/, Qwen3.5-4B/, Qwen3.5-9B/, Qwen3.6-35B-A3B/
VZ_WEIGHTS_ROOT=/data/models bash run/bench_grid.sh ./raw_mygpu
#    restrict it if you wish, for example one model and one mode:
#    MODELS="qwen35_9b:Qwen3.5-9B" MODES="balanced" VZ_WEIGHTS_ROOT=/data/models bash run/bench_grid.sh ./raw_mygpu

# 2. medians, spread and the neutral measurement file
python3 -I run/extract_rows.py --raw ./raw_mygpu --gpu "RTX 4090" --arch sm_89 \
    --measured-at "$(date +%F) (veizik-cuda 1.1.0, tar 43586587)" \
    --prov "my reproduction" --bench-txt my_bench.txt --rows-json my_rows.json
```

- **Drive it only through the installed CLI.** `bench_grid.sh` calls `veizik run` and nothing else;
  `extract_rows.py` only reads the logs. No other engine is involved.
- **Quiet rules.** Use a GPU with nothing else running (`nvidia-smi` shows no other processes), keep
  the board at its default power limit and record it, let the GPU reach steady temperature, and do
  not run other heavy jobs on the host. A run that exits non-zero or prints no timing line is left
  out of the median, and a cell with no completed run is reported as `not_completed`. Repeat the whole grid at least three times if you want a tighter median than the
  committed two-run rows.
- **What a correct run looks like.** Every cell exits 0, reports 21 prompt tokens and 127 decode
  steps, and writes a `gen.txt` whose hash equals the table in §4 (for the same checkpoint
  snapshot). If the prompt-token count differs, the prompt was passed differently — use
  `bench_grid.sh` as written.
- **How close to land.** For the same GPU model and package, decode tok/s should fall within the
  stated spread (largest observed: 1.7 %). Compare only like for like.

| difference | meaning |
|---|---|
| different GPU architecture | legitimate: kernels are per-architecture. Compare only like for like |
| different mode | legitimate: modes are different numerics |
| different driver | may shift timing; should not shift output bytes |
| different package SHA-256 or engine build | **not comparable** — a different build is a different engine |
| different checkpoint snapshot | the output hash may differ; timing should not |
| slower storage or CPU | changes model-load time only; tok/s excludes load |

---

## 7. Verify the committed data

```bash
# the kit's own files are covered by a manifest
cd cuda_deploy/bench/repro_kit && sha256sum -c MANIFEST.sha256

# the rows are plain, inspectable JSON
python3 -I -c "import json; r = json.load(open('../results/RTX4090_rows.json')); print(len(r), r[0])"
```

Every published figure has a row (value, per-run values, spread) and the matching per-run lines in
the `*_bench.txt` of the same GPU. If your reproduction lands within the stated spread, you have
reproduced the board.

---

## 8. Kit contents

| file | what it is |
|---|---|
| `repro_kit/README.md` | the kit's own description |
| `repro_kit/prompts/fact_chatml.txt` | the pinned prompt (ChatML user turn; no trailing newline) |
| `repro_kit/SHA256SUMS` | sha256 of every prompt file; `bench_grid.sh` refuses to run on a mismatch |
| `repro_kit/run/bench_grid.sh` | runs the grid through `veizik run` and writes one log per run |
| `repro_kit/run/extract_rows.py` | turns the logs into `*_bench.txt` and `*_rows.json` (reads timing, memory, exit code and output hash only) |
| `repro_kit/MANIFEST.sha256` | sha256 of the kit files |
