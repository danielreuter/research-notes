---
cursor:
  subagentId: "bc-049fc756-e63b-5b43-af14-0e5a94a2422d"
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T17:22Z
---

# [#582](https://github.com/danielreuter/verity/pull/582) binds sm_120's CUTLASS block-FP8 GEMM as `ScaledMmFp8Block_v2{DOT=BlackwellE4m3QmmaDot32}` (head `82545853`, on #565); tests and circuit-check pass

Step 3 of your 15:23Z GO, from the capture in my 16:55Z handoff (Kueue 273).

- **Why it matters beyond coverage:** on main, the FP8 block rule has no target check. On cc 12.0 it binds `ScaledMmFp8Block_v1`, whose step is Hopper's; the capture shows that wrong on 7,615 of 119,016 coordinates.
- **What it adds:**
  - `ScaledMmFp8Block_v2{K,N,G,DOT}` and its shared-per-block restatement, which are v1's bodies with the step as a static;
  - `targets.fp8_block_dot`: the target's `fp8_dot`, which is the sm_120 step on `blackwell_consumer` and None on cc 9.0, so H100 keeps v1 and no digest moves;
  - the rule, at v2, binds the role `scaled_mm_fp8_block_dot`;
  - a replay row, and a 170 KB in-repo fixture of served PRO 6000 words (one row per dispatch config).
- **Runs:** circuit-check `r20260930-171125-33d9`: 0 new failures, and v1's known per-coordinate recompute also applies to v2. pytest `r20260930-171522-2196`: rc 0 (the FP8 program tests, the FP8 replay tests, lint and the gates).
- **Stack:** #582 → #565 (#516 restacked) → #515 → #487 → main. They land in that order.
- **Next, unless you redirect:**
  1. The pin: block-FP8 rtxpro6000 workloads declaring `target.fp8_block_gemm = "cutlass"`.
  2. The 7 FP8 vLLM deployments from a pre-merge branch (main + #487 + #515 + #565 + #582 + #557), campaign `overnight-sep30`, labelled as your GO says.
  3. For which 7, I'll ask the epoch-run lane for its FP8 list, or use #469's pins × B1/B8. Say if you'd rather pick them.
