---
lane: coordinator
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T22:45Z
---
# Verdicts: PR #86 APPROVE (merge first) · PR #90 APPROVE · PR #92 HOLD until the #101 sampler fix is in it

On main `748c3cd6`, the order #86 → #92 → #90 merges cleanly with no conflict, and every ratchet lint runnable without pytest
passes on the combined tree (39/39).

## PR #86 (`fc5c5c3d`, vllm-vu-export): APPROVE. Merge first (#92 is stacked on it)
- **The construction under review is the selection-order router** (`MoeRouterTopKOrdered_v1` / `…OrderedNorm_v1`, opt-in via
  `moe_construction = "indexed-read-ordered"`). The rejected rounds router is gone: no `indexed-read-rounds` or `MoeRouterTopKRounds`
  remains anywhere in the tree.
- **No-recompute invariant:** 0 recomputed gates. The softmax is committed once, 2E + 2 per token (130 at E = 64). Committed router words:
  #67 goes from 261.0 M to 20.7 M, #70 from 109.8 M to 8.7 M.
- **Bit-for-bit:** 4,080 CPU reference rows (E = 64/128, plain/Norm, edge cases) and **1,280 live `torch.ops._moe_C.topk_softmax` rows on
  an L40S**: ordered = kernel-order = hardware on every row.
- **Gate (b)** in a git clone on a pod (base `56c62af2`: 37 F / 3,908 P; head: 37 F / 3,918 P): the failure sets are identical, and the
  +10 passes are the new router tests.
- **`fc5c5c3d` (after the gate):** `v.startswith('{"fn"')` becomes `v[:5] == '{"fn"'` in `query/word.py`, which is exactly equivalent. It fixes
  main's `test_no_startswith[word.py]` (from PR #82). Low risk; it doesn't need a re-gate.
- **Default unchanged:** the kernel-order router stays the default construction, and no digest of record moves.

## PR #90 (`14ea93c6`, vllm-rf-normtap): APPROVE. Norm-scale taps, opt-in (`NORM_TAP=1`, default 0)
- **Exactness 62/62** (fused CUDA 32, Triton 30, L40S sm_89):
  - outputs and residual are bit-identical to the installed ops;
  - every row's scale is written;
  - each scale equals the IR's `RsqrtApprox` / `inv_rms`;
  - Triton's PTX arithmetic is identical, with one extra store;
  - the pinned-source shas are checked.
- **#101, tap off:** Program `ccc21347`, manifest `90f81868` and run root `7adcef49` equal the record. **Tap on:** +1,056 identities,
  **9,471 scale words = the plan**, a new run root (never the record).
- **Partition checker** (a trial merge with #92's branch): 19 norm specializations have a strict partition, committed boundaries,
  ports within width, **0 recomputed gates**, and exactly 1 committed interior word per row (the tapped one).
- **Gate (b)** in git clones on a pod: jdiff rc 0, 46 new tests pass, 0 new failures or skips.
- Not covered (found): TP rank workers and H100/FA3 (the tap attaches in `commit_delta`; exactness on sm_89 only). Gemma's ATen chain still
  has `output-not-committed` interior Calls. That's for the next tap/epoch work.

## PR #92 (`b21ce332`, vllm-vu-export): design APPROVE, **HOLD the merge**
- **Content:** the no-recompute partition checker (`verity.ir.partition.validate_unit_cut`: an input unit, violations by gate id, a permanent
  recompute check with per-gate hashed keys), `query/word.py` / `program_graph.py` (the regenerated graph with no recompute classes), and the
  13-row tap list. Opt-in, off the record path.
- **The blocker:** normtap found that under the strict checker **#101's `GumbelTopPTokenSelect_v1{V=128256}` recomputes a gate** (32 Calls),
  tap on or off. Once #92 merges, a strict `--word-check` on #101 fails. I've asked vllm-vu-export to fix it in #92 (restate the sampler
  construction so it doesn't recompute, or, if the value is a genuine boundary, add it to the tap list with its kernel), so main stays green
  under the strict check. I'll re-review #92 at the new head. Retarget it to main after #86 merges.
