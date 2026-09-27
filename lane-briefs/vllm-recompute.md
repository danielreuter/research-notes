---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-rf-recompute (the two cross-unit recomputes cross-call-check found: FP8 block scales on #74, Gemma's norm weight + 1 on #57)

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM refactor lane `vllm-rf-recompute`: remove the two real recomputes the no-recompute checks found, as opt-in constructions
> that keep every digest of record fixed. First read
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md` and do its section 1. Then read
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md` (it overrides the setup page for vLLM
> lanes: the no-waiting rule, the gate (b) git-clone procedure, `sampled_proofs` on PYTHONPATH, and **the partition checker with 0 recomputes
> in every review**), then your brief `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-recompute.md`.
> Write your first checkpoint (`research notes checkpoint vllm-rf-recompute open "..."`) within 10 minutes.

## Context
The rule (Daniel, locked; `$STORE/docs/project-context.md`): every gate is in exactly one unit, and every value crossing a unit boundary is
committed; nothing is computed twice. The findings come from vllm-cross-call-check:
`$STORE/internal/lanes/vllm-coordinator/20260927T0300Z-handoff-from-vllm-cross-call-check-cross-call.md`. They show up with PR #98's
`unit_rule` member check and `query.cross_call` (use #98's tree, or main once it merges).

1. **#74 (qwen3-4b-fp8, H100): the FP8 block scale product.** `ScaledMmFp8Block_v1` (`fp8.ScaledMmFp8BlockCoordinate`) computes
   `F32Mul(sx[kb], sw[kb])` in every coordinate of a 128-column weight block: 127 copies per (weight block, kb), over 4 Definitions,
   144 groups and 581,040 Calls, 113.6 G gates computed again.
   - **Fix:** compute each block's scale products once, in a node the coordinates read, and commit them.
   - **Serving:** say where the committed products come from: a host-side computation from the committed `sx` / `sw` with the IR's F32
     semantics (as `vocab_range_source` does), or a store in the FP8 kernel. The product must equal the kernel's operand bit for bit;
     check the kernel source for how it forms it.
2. **#57 (gemma2-2b): the norm weight + 1.** `AddScalarBf16_v1{N=2304,C=1}` in Gemma's ATen norm chain is issued at every engine step:
   T × 105 copies of 105 distinct values per request Program, 102.6 M gates computed again over 8 request Programs.
   - **Fix:** the Build issues the `+ 1` once per norm, and every step reads the committed value.
   - **Serving:** it is a weights-derived value, committed once per norm at load; say how the committer produces it.

## Constraints
- **Opt-in, digests of record fixed.** Both fixes change Programs (#74's FP8 Definitions, #57's request Programs). Land each behind a
  construction selector (like `moe_construction` / #101's `SHARED_GREEDY`), with the default unchanged. Show with the selector off that the
  #74 and #57 Program digests, manifests and every other row are byte-identical to main.
  - Switching the record is a re-baseline epoch item: root decides.
- **Acceptance per fix:**
  - the partition checker (`Q_word_v1{…,R=no-recompute}` with #98's member check, plus `query.cross_call`) shows 0 recomputes for the
    row with the selector on;
  - the committed words are counted;
  - outputs are bit-identical to the old construction on edge vectors (circuit-check style: NaN, ±inf, ±0, subnormals, E4M3 edges for FP8);
  - gate (b).
- **CPU first.** #74's serving-side check may need an H100 (FP8 block kernel), and #57's may need an L40S. Hand off an estimate before
  any pod; root approves spend. The day stops at $760.

## Deliverables
One PR per fix, and merge-ready handoffs to `$STORE/internal/lanes/vllm-coordinator/` with the checker output, the digest A/B, the tests
and gate (b).
