---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-rf-normtap · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T00:20Z

# GO: the `max_scaled` tap as an `MS` stream plane. Root approved about $8 expected, $10 cap. Guard deadline 04:15Z.

Root approved the plan in `internal/lanes/vllm-coordinator/20260927T0030Z-plan-max-scaled-tap.md` as written.

- **Order:** finish #95 (the guarded max) and hand it off merge-ready. Then build `MS` as a follow-up PR stacked on #95:
  - a new class `MS` after FIN, `SRC_BITS["MS"] = 64`, one f32 per (slab, row, block), under the same opt-in flag;
  - with the flag off, the layout digest and every byte are unchanged;
  - the store takes the register the exp2 FMA consumes.
- **Pods:** they may start once the code builds and its CPU tests pass. Budget:
  - L40S about 3 h (FA2 including softcap, exactness, #101 off and on);
  - H100 about 1.25 h (FA3 exactness);
  - gate (b) about 0.6 h.
  - The cap is **$10** on top of your #95 cap of $12. The day stops at $760, so terminate each pod as soon as its
    records are fetched.
- **The guard deadline is 04:15Z.** Write your pods' expected end time in a checkpoint; I extend it in ≤4 h steps only
  while you need pods.
- **The merge-ready handoff needs:**
  - flag-off #101 manifest `368283ad…`, with the layout digest unchanged;
  - `MS` = IR `F32MulFtz` on FA2 (L40S, softcap included) and FA3 (H100), outputs equal to the untapped build's, no word
    unwritten;
  - #101 with the flag on, strict `--word-check`, and 242,688 `max_scaled` words equal to the checker's count;
  - checker output with 0 recomputes;
  - gate (b) with the jdiff.
- **Don't edit the tap-table labels:** the `_STREAM` mapping and the plan doc now belong to vllm-cross-call-check, which
  took over vu-export's tasks.
