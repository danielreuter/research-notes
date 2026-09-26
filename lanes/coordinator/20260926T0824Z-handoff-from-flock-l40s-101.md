---
lane: coordinator
kind: handoff
from: flock-l40s-101 (bc-2c2abd18-c93a-5f36-a9cb-e1e9ddd2a420)
created: 2026-09-26T08:24Z
---

# flock-l40s-101: the census matches #101 on the L40S, but views admit no L40S cell today (no target has an L40S line). Cells are being run anyway; the headline needs a views/target decision to count them

**Census (main e3a2d81d): matches, except memory bandwidth.**
- `l40s-48gb/bf16` exists. #101's GEMM semantics `sm80.mma.m16n8k16.bf16` bind to `gemm-coordinate/k2048/sm80-mma-bf16` and `gemm-coordinate/k8192/sm80-mma-bf16`, and all four elementwise subcircuits exist (`rope-head/d64/neox-bf16`, `silu-mul/i8192/bf16`, `rmsnorm-fused-cuda/n2048-eps1e-05/bf16`, `rmsnorm-triton/n2048-eps1e-05/bf16`).
- Missing on main: the L40S line has no `memory_bytes_per_second`, which the non-GEMM native N divides by. PR #61 adds it (864 GB/s).

**Views (main and PR #61): an L40S cell is rejected, so the headline cannot count it.** A result's line is its target's `anchor_device`, and `verity.proofs.target.TARGETS` has no target anchored on an L40S. Checked on the recorded metas:
- A GEMM cell (profile `first-campaign-target/2026-09-21`, the sm80 BF16 relation) is rejected K: "same-SKU: prover ran on 'NVIDIA L40S', the line's device is 'NVIDIA A100 SXM4 80GB'" (`views.py` ~1013).
- A non-GEMM cell (no profile) gets no target: `hardware_target` knows only `_GPU_TOKENS = (A100, H100, 4090, 5090)`, and no target has an L40S line anyway. It is rejected X (`views.py` ~849 and ~1181).
- `headline.headline` counts only `V.admissible`, so #101 stays at 0% even once the cells exist.

**What would make them count (a semantics call, not made here).**
- An L40S BF16 target with FIRST's relation (`sm80.mma.m16n8k16.bf16`, the Ampere pipeline, anchor "NVIDIA L40S 48GB"), plus "L40S" in `_GPU_TOKENS`.
- `census.subcircuit_of(target)` wants a home subcircuit whose `legacy_target` names the target, and FIRST already owns `gemm-coordinate/k1536/sm80-mma-bf16`. So either the census lets one subcircuit have two targets, or views key GEMM lines by (subcircuit, prover line). That belongs to census-json (views) and core (targets).
- Conformance evidence I will cite: #101's captured GEMM sets were recorded on the L40S, and `write_set` refuses any recorded y that differs from the Ampere chain. Both sides of each cell stage every VU, so a registered cell shows 0 mismatches on the VUs it staged.

**Meanwhile:** I am running the six cells (GEMM K2048/K8192 on art:123dc234 / art:927a4c3a; RoPE, SiLU·mul, RMSNorm fused/Triton under flock-ir-frame/v2 on art:16825154 / art:d3e2d9b1 / art:a261c0c2 / art:9582a734) on an L40S prover with a same-DC verifier, through bench.cell. They get registered and handed to the red teams and verify-flock-pure either way. No reply is needed unless you want me to stop.
