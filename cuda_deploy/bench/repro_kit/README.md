# Repro kit — pinned inputs and scripts

Everything needed to re-measure the rows in `../results/` on your own GPU, driven only through the
installed `veizik` CLI. The guide is [`../REPRODUCIBILITY.md`](../REPRODUCIBILITY.md).

```
repro_kit/
  README.md           this file
  SHA256SUMS          sha256 of every prompt file (bench_grid.sh enforces it)
  MANIFEST.sha256     sha256 of the kit files
  prompts/
    fact_chatml.txt   the pinned prompt: a ChatML user turn, no trailing newline (21 prompt tokens)
  run/
    bench_grid.sh     runs the grid through `veizik run`; writes one log per run
    extract_rows.py   turns the logs into *_bench.txt and *_rows.json
```

Verify before reproducing:

```bash
( cd prompts && sha256sum -c ../SHA256SUMS )     # the prompt
sha256sum -c MANIFEST.sha256                      # the kit files
```

Run (Linux, package installed and activated, checkpoints in one folder):

```bash
VZ_WEIGHTS_ROOT=/data/models bash run/bench_grid.sh ./raw_mygpu
python3 -I run/extract_rows.py --raw ./raw_mygpu --gpu "RTX 4090" --arch sm_89 \
    --measured-at "$(date +%F) (veizik-cuda 1.1.0, tar 43586587)" --prov "my reproduction" \
    --bench-txt my_bench.txt --rows-json my_rows.json
```

The committed rows are valid for the build named in their `measured_at` and `prov` fields (see
[`../../RELEASE_NOTES.md`](../../RELEASE_NOTES.md) for the shipped package). A kit run on a different
package SHA-256 is a different engine: compare it by method, not by value.
