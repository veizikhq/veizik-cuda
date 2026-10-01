# veizik-flux — CUDA / Linux

FLUX.1 text-to-image, a self-contained **sealed** engine for NVIDIA GPUs (Linux x86_64). No CUDA toolkit,
no Python, no PyTorch, no compiler on the host — just an NVIDIA driver. The engine runs only on an
**activated device**; GPU kernels ship encrypted at rest and are delivered a device-bound key at activation.

**Get the bundle from [Releases](../../releases).** Verify its `sha256`, then:

```
tar xzf veizik-flux-1.0.3-linux-x86_64.tar.gz
cd veizik-flux-1.0.3-linux-x86_64
./veizik run flux1dev --out ~/veizik-out --prompt "a red fox in snow"
```

Weights are **not** included (point a run at a FLUX.1-dev snapshot with `--weights DIR` / `VZ_WEIGHTS` / the
Hugging Face hub; the FLUX.1[dev] weights carry Black Forest Labs' license). Per-architecture precision and
requirements are in the bundle's `README.txt`; integrity self-checks at every launch (`bin/vzseal`).
