# Veizik CUDA — measured data and how to reproduce it

**Own-numbers-only policy.** Every figure here was measured by us on the shipped bytes. Each row
names the package, the GPU, the mode, and the operating point. We do not publish comparisons against
other engines, and we do not publish a figure we have not measured on the exact package we ship.

---

## 1. How to read a row

A row is only meaningful with all of: **package SHA-256 · GPU · driver · mode · operating point**
(resolution + steps for image, resolution + frames + steps for video, context + generated tokens for
text). A number without those is not a result.

---

## 2. Measured results

Results are published per release, keyed to the package SHA in
[`../RELEASE_NOTES.md`](../RELEASE_NOTES.md).

| Family | GPU | Mode | Operating point | Metric | Value |
|---|---|---|---|---|---|
| _(populated at each release from the measurement run on the shipped bytes)_ | | | | | |

> A release that has not been measured on the shipped bytes ships with this table marked
> **not measured** for that cell rather than carrying a number from an earlier build. Numbers do not
> carry across a rebuild.

---

## 3. Reproducing a row

1. Install the exact package named in the row and verify its SHA-256 (`README.md` §2).
2. Activate the device (`README.md` §4).
3. Take the pinned inputs from [`repro_kit/`](repro_kit/) — prompts, seeds, and the input manifest.
4. Run the command printed next to the row, unchanged.
5. Compare against the recorded output hash in the kit manifest.

Differences to expect, and what they mean:

| Difference | Meaning |
|---|---|
| different GPU architecture | legitimate; kernels are per-architecture. Compare only like-for-like |
| different mode | legitimate; modes are different numerics |
| different driver | may shift timing; should not shift output bytes |
| different package SHA | **not comparable** — a different build is a different engine |

---

## 4. Measurement method

- Timings are taken in-process, excluding one-time bundle bring-up unless the row says otherwise.
- Memory figures are peak resident VRAM for the run.
- Where a GPU can be power-capped, the cap is stated; a power-depressed measurement is not published
  as a headline figure.
- Each published figure is the median of repeated runs; the repeat count is stated per row.

---

## 5. Repro kit

[`repro_kit/`](repro_kit/) holds the pinned inputs and a SHA manifest so a run can be checked
end-to-end. See its `MANIFEST.sha256`.
