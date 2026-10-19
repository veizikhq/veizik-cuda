# Repro kit — pinned inputs

Pinned prompts, seeds and input files for the measured rows in `../REPRODUCIBILITY.md`, plus
`MANIFEST.sha256` so every input can be verified before a run.

```
repro_kit/
  MANIFEST.sha256     # sha256 of every input in this kit
  prompts/            # exact prompt text, one file per row
  inputs/             # image/latent/mask inputs where a row needs them
  run/                # the exact command per row
```

Verify before reproducing:
```bash
sha256sum -c MANIFEST.sha256
```

Populated per release from the measurement run on the shipped bytes. A kit is only valid for the
package SHA it was produced against — see `../../RELEASE_NOTES.md`.
