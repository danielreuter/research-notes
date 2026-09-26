---
cursor:
  subagentId: "bc-eab8c043-7f1c-5a4d-802c-0b9aa73f289b"
---

# Handoff from vllm-vu-export: MoE router restated. PR #86, corrected at 20:45Z; needs your re-review (20260926T2025Z)

> **Correction (20:45Z).** The rounds statement described below recomputed the softmax in every round and weight unit (18,144
> recomputed gates per token), so its "0 committed" broke the no-recompute invariant. PR #86 now carries `MoeRouterTopKOrdered_v1` /
> `MoeRouterTopKOrderedNorm_v1` (opt-in `moe_construction = "indexed-read-ordered"`). It computes the softmax once and commits
> 2E + 2 values per token; each round takes the expert after the previous selection in the kernel's order. Committed router words:
> **#67 261.0 M → 20.7 M, #70 109.8 M → 8.7 M** (kernel order → selection order, both under the no-recompute rule). Your approval
> covered the old construction, so please re-review. The lines below are corrected in place.

lane: vllm-vu-export · kind: handoff · from: vllm-vu-export (agent bc-eab8c043) · created: 20260926T2025Z · re: `20260926T1945Z-handoff-from-vllm-coordinator.md`

**Merge request: PR #86** (`cursor/moe-router-rounds-289b`, head `3c8f5f53`, base `main`). Re-review first; then pass it to the research coordinator.

- **What it adds:** `MoeRouterTopKOrdered_v1` / `MoeRouterTopKOrderedNorm_v1{E,TOPK,VPT}`, built from `MoeRouterProbs_v1` (the softmax, once),
  `MoeRouterFirst_v1`, `MoeRouterNext_v1` (the experts after the previous (p, id) in the kernel's order, then the same scan) and
  `MoeRouterPick_v1` (`p[id]`).
- **Opt-in** through `moe_construction = "indexed-read-ordered"`: the MOE-01 rules, with only the router kind swapped. The Build, Match fold (`MoEFusedExpertsOrdered`) and replay rows are wired.
  - The kernel-order routers encode byte-identically; a test pins their digests. No digest of record moves.
- **Bit-for-bit evidence, CPU:**
  - the reference evaluator gives **4,080 rows (per configuration, 1,000 random and 20 edge rows)** (±0, all −inf, all NaN, +inf, NaN first, exact and near ties, `expf` overflow, underflow, subnormals, max finite) at E = 64 and 128, in plain and Norm: **0 unequal**;
  - the replay self-check (numpy row evaluator against the new Definitions): 256 rows, 0 mismatches.
- **Invariants** (the no-recompute checker, on the no-recompute branch): 0 recomputed gates, every unit output ≤ 32 bits, the
  softmax committed once: 2E + 2 per token (130 at E = 64; 267 for Qwen3's Norm router at E = 128).
- **Committed router interior words** (kernel order → selection order, both under the no-recompute rule): **#67 261.0 M → 20.7 M**,
  **#70 109.8 M → 8.7 M**.
- The committed softmax is itself a new commitment: serving must store it from `topk_softmax` (the tap list, plan doc §5).
- **Gap:** no replay against recorded #67 / #70 router words, because none exist to replay. The committed stores weren't preserved, and the #67 export drew nothing. The kernel-order Definition's kernel exactness (lane ov-moe, 192/192 recorded words, and the R13 xcheck) carries over through the equality above.
  - Optional: a live `topk_softmax` comparison on an L40S, about 20 minutes and under $1. **No pod was created**; it waits for your GPU confirmation.
- **Lints:** P01–P12, by-name and dead modules pass locally through a pytest stand-in. Please run the real gate on your pod.
- **Spend:** $0. The epoch and the recompute threshold are untouched.
- **Evidence:** `research-notes/lanes/vllm-vu-export/evidence/moe-router-rounds/` (`router_eq.json`, `router_counts.json`, the script).
