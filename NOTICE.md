# Veizik for NVIDIA GPUs (Linux) — Third-Party Notices

Copyright © 2026 LinkPick. All rights reserved. Veizik is a brand of LinkPick.

## 1. Redistributed with these packages

Nothing. Every file in the two packages was built by LinkPick: the engines and their
sealed GPU code, the launchers, the `veizik` command, the installer, the model catalogue
and the checksums. `SHA256SUMS` in the Qwen package and `SHA256SUMS.vz` in the WAN package
list the complete set.

**No model weights are included, and no model publisher's inference code.**

## 2. Required at run time, not redistributed

The engines need only the NVIDIA driver (`libcuda.so.1`) and the system libraries of an
ordinary Linux installation. Their use is governed by their own licences, not by this
notice. No CUDA toolkit, Python interpreter or package manager is required, and none is
installed.

## 3. Model checkpoints — yours, under their own licence

The engines read a checkpoint you obtained yourself, under the licence its publisher
attached to it. You accept that licence from the publisher, not from us. The model cards'
acceptable-use terms apply to your use of the weights and of what you generate with them.

### Language models (veizik-qwen-cuda 1.0.0)

| Checkpoint | Publisher | Licence |
| --- | --- | --- |
| `Qwen/Qwen3.5-0.8B` | Alibaba Cloud | Apache-2.0 |
| `Qwen/Qwen3.5-2B` | Alibaba Cloud | Apache-2.0 |
| `Qwen/Qwen3.5-4B` | Alibaba Cloud | Apache-2.0 |
| `Qwen/Qwen3.5-9B` | Alibaba Cloud | Apache-2.0 |
| `Qwen/Qwen3.6-35B-A3B` | Alibaba Cloud | Apache-2.0 |

### Video models (veizik-wan 1.2.0)

| Checkpoint | Publisher | Licence |
| --- | --- | --- |
| `Wan-AI/Wan2.1-T2V-1.3B-Diffusers` | Wan-AI (Alibaba) | Apache-2.0 |
| `Wan-AI/Wan2.1-T2V-14B-Diffusers` | Wan-AI (Alibaba) | Apache-2.0 |
| `Wan-AI/Wan2.2-T2V-A14B-Diffusers` | Wan-AI (Alibaba) | Apache-2.0 |
| `Wan-AI/Wan2.2-I2V-A14B-Diffusers` | Wan-AI (Alibaba) | Apache-2.0 |

The Wan checkpoints include their umT5-XXL text encoder, tokenizer and Wan VAE, under the
same licence (<https://huggingface.co/Wan-AI>, <https://github.com/Wan-Video>).

### Wan2.2-Lightning (optional 4-step distillation LoRA) — lightx2v
The optional Lightning 4-step LoRA weights used by the `wan22_*_a14b_lightning` models are
USER-SUPPLIED at render time (fetched into the user's weights directory by `veizik pull`); they are
NOT distributed in this release package.
- Source: lightx2v — <https://huggingface.co/lightx2v/Wan2.2-Lightning>
- Weights: Wan2.2-I2V-A14B-4steps-lora-rank64-Seko-V1, Wan2.2-T2V-A14B-4steps-lora-rank64-Seko-V1.1
- License: Apache License 2.0 (see upstream LICENSE.txt)
- The upstream project builds upon and reuses code from Wan2.1 and Wan2.2 (Apache License 2.0).

## 4. Published methods the WAN engine implements

The WAN engine implements these methods from their publications and reference
implementations. No code was copied.

- UniPC multistep sampling with flow sigmas, as in the diffusers `UniPCMultistepScheduler`
  (Apache-2.0).
- FlashAttention-2 style tiled attention (Dao, 2023).
- The diffusers `WanPipeline` (Apache-2.0).

## 5. Trademarks

NVIDIA and CUDA are trademarks of NVIDIA Corporation. Qwen and Wan are trademarks of their
owners. Linux is a trademark of Linus Torvalds. Use here is nominative — naming what this
runs on and what it reads — and implies no endorsement or affiliation.

Questions about these notices: <https://veizik.com>
