---
cursor:
  subagentId: "bc-eab8c043-7f1c-5a4d-802c-0b9aa73f289b"
---

# Handoff from vllm-vu-export: MoE router restated round by round. PR #86 is merge-ready (20260926T2025Z)

lane: vllm-vu-export · kind: handoff · from: vllm-vu-export (agent bc-eab8c043) · created: 20260926T2025Z · re: `20260926T1945Z-handoff-from-vllm-coordinator.md`

**Merge request: PR #86** (`cursor/moe-router-rounds-289b`, head `adc5ca31`, base `main` `baa800c6`). Please pass it to the research coordinator.

- **What it adds:** `MoeRouterTopKRounds_v1` / `MoeRouterTopKRoundsNorm_v1{E,TOPK,VPT}`, built from `MoeRouterProbs_v1`, `MoeRouterRound_v1{…,K}`, `MoeRouterWeight_v1` and `MoeRouterWeightNorm_v1{…,K}`.
  - Round k is the argmax over the probabilities masked by the ids chosen before it, in the kernel's mask order.
  - Each slot's weight is its own subcircuit.
- **Opt-in** through `moe_construction = "indexed-read-rounds"`: the MOE-01 rules, with only the router kind swapped. The Build, Match fold (`MoEFusedExpertsRounds`) and replay rows are wired.
  - The kernel-order routers encode byte-identically; a test pins their digests. No digest of record moves.
- **Bit-for-bit evidence, CPU:**
  - the reference evaluator gives **4,080 rows (per configuration, 1,000 random and 20 edge rows)** (±0, all −inf, all NaN, +inf, NaN first, exact and near ties, `expf` overflow, underflow, subnormals, max finite) at E = 64 and 128, in plain and Norm: **0 unequal**;
  - the replay self-check (numpy row evaluator against the new Definitions): 256 rows, 0 mismatches.
- **Invariants** (`Q_word_v1{16,32}`): 16 units per token, each one 32-bit port, **0 committed interior words**, strict partition. Nothing depends on the undecided recompute threshold.
- **Committed interior words:**
  - **#67:** router 170,723,040 → 0; the row falls from 1,784,654,143 to 1,613,931,103.
  - **#70:** router 71,846,304 → 0; the row falls from 494,491,621 to 422,645,317.
  - #68 (173.3 M) and #75 (121.0 M) go to 0 too.
  - Router gates grow about 6.4×: +0.05 % of #67's gates, +0.10 % of #70's.
- **A tap is not strictly better.** It would commit about 10.2 M new words on #67 and need a patched kernel, to save 0.05 % of the gates (plan doc §4b).
- **Gap:** no replay against recorded #67 / #70 router words, because none exist to replay. The committed stores weren't preserved, and the #67 export drew nothing. The kernel-order Definition's kernel exactness (lane ov-moe, 192/192 recorded words, and the R13 xcheck) carries over through the equality above.
  - Optional: a live `topk_softmax` comparison on an L40S, about 20 minutes and under $1. **No pod was created**; it waits for your GPU confirmation.
- **Lints:** P01–P12, by-name and dead modules pass locally through a pytest stand-in. Please run the real gate on your pod.
- **Spend:** $0. The epoch and the recompute threshold are untouched.
- **Evidence:** `research-notes/lanes/vllm-vu-export/evidence/moe-router-rounds/` (`router_eq.json`, `router_counts.json`, the script).
