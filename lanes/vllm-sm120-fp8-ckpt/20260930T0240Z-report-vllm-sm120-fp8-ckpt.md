---
lane: vllm-sm120-fp8-ckpt
kind: report
created: 2026-09-30T02:40Z
status: open
---

CHECKPOINT 59bde0ce (03:40Z) [open] commits e6c2da8e (bootstrap makes recipe pins) + 59bde0ce (9 FP8 pins, all re-made identical with the final code). Pod estimate written: vy-sm120-fp8-ckpt-1, ~1 GPU-h (~$2.1) for an sm_120 load smoke + 2nd-machine reproduction. 7B/14B/32B pins in progress on VM.
CHECKPOINT 1a2a6ef0 (03:25Z) [open] PR #469 draft (recipe, 14 CPU tests; lints P6-P12 + by-name + dead-modules pass). Pinned on VM so far: QWEN05 TINYLLAMA LLAMA32_1B B1 QWEN15_INSTRUCT GEMMA2_2B PHI3_MINI MISTRAL7B FP8, each re-made identical. Next: 7B/14B/32B, manifest + configs + profile fixtures. No pod yet.
CHECKPOINT d090c814 (03:09Z) [open] recipe verity-fp8-block128/v1 (data-free, amax/448 per 128x128 block, RNE e4m3, deterministic container) written; QWEN05 made on VM in 6s, verified by the reference safetensors parser, accepted by quant_refusal. Downloads under way; next: pins for 13 models + tests.
CHECKPOINT d090c814 (03:04Z) [open] recipe verity-fp8-block128/v1 (data-free, amax/448 per 128x128 block, RNE e4m3, deterministic container) written; QWEN05 made on VM in 6s, checked by the reference safetensors parser. BF16 downloads under way; next: pins for 13 models + tests.
CHECKPOINT d090c814 (03:03Z) [open] recipe verity-fp8-block128/v1 (data-free, amax/448 per 128x128 block, RNE e4m3, deterministic container) written; QWEN05 made on VM in 6s, checked by the reference safetensors parser. BF16 downloads under way; next: pins for 13 models + tests.
CHECKPOINT d090c814 (02:49Z) [open] hub survey done: exact-format (fp8 block128 dynamic) releases exist only for Qwen3-4B-2507 (pinned) and Qwen3-30B-A3B (Qwen official); others community compressed-tensors per-channel. Qwen FP8 not reproducible from BF16 (scales +-0.33%). next: recipe module + CPU tests.
CHECKPOINT d090c814 (02:44Z) [open] budget line confirmed live (coordinator note 02:40Z). Read the pins (manifests/checkpoints.json, append-only) and model.quant_refusal (block-128 dynamic e4m3 only). 17 representable models; next: hub survey of FP8 releases per model.
CHECKPOINT d090c814 (02:40Z) [open] started (agent bc-f23795f4); read brief/common/contract; next: survey FP8 checkpoints for the matrix's representable models (CPU only). No pod until coordinator confirms vy-sm120- line.
