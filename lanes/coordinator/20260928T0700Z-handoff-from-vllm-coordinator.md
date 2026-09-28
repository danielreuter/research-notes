---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T07:00Z

# Merge requests for the re-baseline epoch: S2 #233, S3 #242, and #39's `GemmBias` #244. All APPROVE.

All three are on main 6746f408 and merge cleanly pairwise. **Order:** #233, then #242; #244 is independent. These are the epoch's
switch PRs, so they move digests of record by design. The rows are re-recorded on them.

| PR | Head | What | What moves |
|---|---|---|---|
| **S2 #233** | `c0db84e1` | Program ids use a declared, versioned `DERIVE_SOURCE` (for example `verity-vllm/engine-step/v1`) instead of the wrapper's module path | every row's step, request and workload Program digests, through `SRC` only; nothing structural. The lane's CPU A/B on stored #57/#73/#74 descriptors: every digest recomputes exactly and moves |
| **S3 #242** | `8f567db6` | the four taps default on (`=0` / `--no-*` for A/B); rows attach a tap only where their manifest names the family; TP rows carry the guarded max and norm tap; the bootstrap builds the tap libraries | every row's manifest and run root (norm scales, the `MS` class on attention streams, the router softmax on MoE rows once S4 lands, the vocab range on #70/#75). Program digests don't move. CPU A/B: #73 +1,305, #57 +5,565, #74 +290 identities |
| **#244** (for #39) | `b0b4b438` | `GemmBias_v1{K,N}`: a biased linear's `Gemm_v1` whose only reader is its bias add becomes one Definition, decided from the dataflow; frontend + fold + row kernel + lowering | only #39 among the 13 (the only row with `BiasAdd_v1`). A real Qwen2.5-1.5B Build and Match: Call boundaries 8,036 → 0, Match PASS, GM-01 PASS |

- **Tests:** my combined jdiff of main against main + #233 + #242 + #244, over `tests/{program,check,pipeline,query,commit,acquire,
  properties,regression}`, the lints, by-name, imports and dead-modules:
  - 3,173 tests, 5 new ones pass, and 0 changed outcomes.
  - The only new entries are `test_derive_source_id.py` and `test_gemm_bias.py`, which fail collection here because they import torch
    and this VM has none. The lanes ran them with torch.
- **G0 still open:** #197 and #231 (#231 is held for its three lint fixes), the `AmpereBF16TcDot16` re-key (no word from bc-e373566b
  yet), and #111; then S4 and S1 (#232).
