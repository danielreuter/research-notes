---
lane: vllm-sm120-fp8-ckpt
kind: report
created: 2026-09-30T02:40Z
status: open
---

CHECKPOINT d090c814 (03:04Z) [open] recipe verity-fp8-block128/v1 (data-free, amax/448 per 128x128 block, RNE e4m3, deterministic container) written; QWEN05 made on VM in 6s, checked by the reference safetensors parser. BF16 downloads under way; next: pins for 13 models + tests.
CHECKPOINT d090c814 (03:03Z) [open] recipe verity-fp8-block128/v1 (data-free, amax/448 per 128x128 block, RNE e4m3, deterministic container) written; QWEN05 made on VM in 6s, checked by the reference safetensors parser. BF16 downloads under way; next: pins for 13 models + tests.
CHECKPOINT d090c814 (02:49Z) [open] hub survey done: exact-format (fp8 block128 dynamic) releases exist only for Qwen3-4B-2507 (pinned) and Qwen3-30B-A3B (Qwen official); others community compressed-tensors per-channel. Qwen FP8 not reproducible from BF16 (scales +-0.33%). next: recipe module + CPU tests.
CHECKPOINT d090c814 (02:44Z) [open] budget line confirmed live (coordinator note 02:40Z). Read the pins (manifests/checkpoints.json, append-only) and model.quant_refusal (block-128 dynamic e4m3 only). 17 representable models; next: hub survey of FP8 releases per model.
CHECKPOINT d090c814 (02:40Z) [open] started (agent bc-f23795f4); read brief/common/contract; next: survey FP8 checkpoints for the matrix's representable models (CPU only). No pod until coordinator confirms vy-sm120- line.
