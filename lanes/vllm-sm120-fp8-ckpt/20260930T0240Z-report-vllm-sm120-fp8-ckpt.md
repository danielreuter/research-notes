---
lane: vllm-sm120-fp8-ckpt
kind: report
created: 2026-09-30T02:40Z
status: open
---

CHECKPOINT 86476296 (04:38Z) [open] smoke r20260930-042207-1591 PASS + preserved: all 8 FP8 pins load+generate on sm_120 (vLLM d9105ea80, batch-invariant env); every FP8 linear = CutlassFp8BlockScaledMMKernel; 30B-A3B = Fp8MoEMethod. WAIT r20260930-041857-e985 (vLLM suite; base done, head running) check-back 04:55Z; then terminate vy-sm120-fp8-ckpt-1.
CHECKPOINT 86476296 (04:22Z) [open] smoke r20260930-035545-6692: bootstrap re-made 6 recipe pins on the pod, all sha256 = pins (2nd-machine repro PASS); my torch gate failed on 'import vllm._C' (not a module in this vLLM; ops load via vllm._custom_ops). Corrected gate PASS: cc 12.0, 188 SMs, sm_120 in torch arch list, cutlass block-FP8 supports sm120. Loads relaunched: r20260930-042207-1591.
CHECKPOINT 86476296 (04:19Z) [open] 86476296 pushed: all FP8 pins registered (hub: QWEN3_30B_A3B_FP8; recipe: 12 dense). WAIT vy-sm120-fp8-ckpt-1 r20260930-035545-6692 (smoke) + r20260930-041857-e985 (vLLM suite base vs head) check-back 05:00Z agent bc-f23795f4. Evidence art:c0afdf95.
CHECKPOINT 59bde0ce (03:58Z) [open] WAIT vy-sm120-fp8-ckpt-1 r20260930-035545-6692 check-back 04:50Z agent bc-f23795f4: sm_120 FP8 load smoke (gate 1 PASS: driver 595.91.07 cc 12.0; bootstrap re-made QWEN05/LLAMA32_1B/TINYLLAMA/GEMMA2 FP8 on the pod, sha256 = pins). First launch r20260930-035334-be70 died on a bad --timeout value. VM: 32B pin running; 7B/14B-Instruct pinned+remade identical.
CHECKPOINT 59bde0ce (03:40Z) [open] commits e6c2da8e (bootstrap makes recipe pins) + 59bde0ce (9 FP8 pins, all re-made identical with the final code). Pod estimate written: vy-sm120-fp8-ckpt-1, ~1 GPU-h (~$2.1) for an sm_120 load smoke + 2nd-machine reproduction. 7B/14B/32B pins in progress on VM.
CHECKPOINT 1a2a6ef0 (03:25Z) [open] PR #469 draft (recipe, 14 CPU tests; lints P6-P12 + by-name + dead-modules pass). Pinned on VM so far: QWEN05 TINYLLAMA LLAMA32_1B B1 QWEN15_INSTRUCT GEMMA2_2B PHI3_MINI MISTRAL7B FP8, each re-made identical. Next: 7B/14B/32B, manifest + configs + profile fixtures. No pod yet.
CHECKPOINT d090c814 (03:09Z) [open] recipe verity-fp8-block128/v1 (data-free, amax/448 per 128x128 block, RNE e4m3, deterministic container) written; QWEN05 made on VM in 6s, verified by the reference safetensors parser, accepted by quant_refusal. Downloads under way; next: pins for 13 models + tests.
CHECKPOINT d090c814 (03:04Z) [open] recipe verity-fp8-block128/v1 (data-free, amax/448 per 128x128 block, RNE e4m3, deterministic container) written; QWEN05 made on VM in 6s, checked by the reference safetensors parser. BF16 downloads under way; next: pins for 13 models + tests.
CHECKPOINT d090c814 (03:03Z) [open] recipe verity-fp8-block128/v1 (data-free, amax/448 per 128x128 block, RNE e4m3, deterministic container) written; QWEN05 made on VM in 6s, checked by the reference safetensors parser. BF16 downloads under way; next: pins for 13 models + tests.
CHECKPOINT d090c814 (02:49Z) [open] hub survey done: exact-format (fp8 block128 dynamic) releases exist only for Qwen3-4B-2507 (pinned) and Qwen3-30B-A3B (Qwen official); others community compressed-tensors per-channel. Qwen FP8 not reproducible from BF16 (scales +-0.33%). next: recipe module + CPU tests.
CHECKPOINT d090c814 (02:44Z) [open] budget line confirmed live (coordinator note 02:40Z). Read the pins (manifests/checkpoints.json, append-only) and model.quant_refusal (block-128 dynamic e4m3 only). 17 representable models; next: hub survey of FP8 releases per model.
CHECKPOINT d090c814 (02:40Z) [open] started (agent bc-f23795f4); read brief/common/contract; next: survey FP8 checkpoints for the matrix's representable models (CPU only). No pod until coordinator confirms vy-sm120- line.
