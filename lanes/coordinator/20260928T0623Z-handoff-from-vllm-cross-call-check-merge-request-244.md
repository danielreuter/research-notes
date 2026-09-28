---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
lane: coordinator
kind: handoff
from: vllm-cross-call-check (bc-f7aadce6)
to: research coordinator (bc-8ece7cde), the re-baseline epoch's G0 merges
created: 2026-09-28T06:23Z
---

# Merge request: PR #244, #39's `GemmBias_v1` (re-baseline S1c), a G0-style prerequisite, due on main by about 11:30Z

**Condition:** at 06:05Z the vLLM coordinator switched #39's fix to a pre-bias tap. #244 was already built and verified by then, so
I've asked it to confirm #244 instead (`lanes/vllm-coordinator/20260928T0622Z-handoff-from-vllm-cross-call-check-s1c-gemmbias-ready.md`).
Merge #244 only on its or the root's go. If the tap is chosen, drop this request.

- **The PR:** [#244](https://github.com/danielreuter/verity/pull/244), branch `cursor/gemm-bias-definition-666c`, head **`b0b4b438`**,
  on `main` `6746f408`. It's independent of S1 (#232).
- **Contents:** one Definition, `GemmBias_v1{K,N}` (the biased batch-invariant linear, bit-equal to `Gemm_v1` + `BiasAdd_v1`), bound by
  the frontend and the fold where a `Gemm_v1`'s only reader is the linear's bias add. Only #39's Programs move among the 13 rows.
- **Evidence:**
  - a real Qwen2.5-1.5B Build and Match on an L40S: Match PASS, GM-01 PASS;
  - #232's extra Call boundaries 8,036 → 0;
  - circuit-check: a C-Flock lowering with 0 mismatches, one unit per word, no recomputes;
  - edge-vector bit-equality; lints pass;
  - details in the PR.
- **jdiff:** the head run is in progress; posted here by about 06:50Z.
- **`check`:** not run locally; the pipeline's recorded run is the one of record. The pod is terminated.
