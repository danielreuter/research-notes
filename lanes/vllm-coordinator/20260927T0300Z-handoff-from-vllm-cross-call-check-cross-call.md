---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: vllm-cross-call-check · kind: handoff · to: vllm-coordinator · created: 2026-09-27T03:00Z

# PR #98 merge-ready: cross-Call check + `unit_rule` member check + pure-wiring fix; the checker's verdict moves on #74 (FP8), and nothing else moves

[PR #98](https://github.com/danielreuter/verity/pull/98), branch `cursor/vllm-cross-call-check-666c` @ `d7f76916` (base `main` `fa662029`, merged in; it merges cleanly with #99 in either order). This covers your 01:35Z priority items 1 and 2, folded into #98 as root asked.

**What it adds**
- `query.cross_call`: the program-level pass (Calls, operand subsets, gates), opt-in through `manifest build|build-global --cross-call-check`.
- `word.unit_rule` compares a separable body's members (`cross_call.members_check`). This closes the gap circuit-checks found: a value two members compute is a `cut` violation (`gate-recomputed`).
- `word.units`: a Call that only rearranges bits returns its inputs, so `DeriveRefBf16ToF32_v1` no longer trips `committed-unread`. This only turns failing cuts into passes.
- `query/call_scope.py` holds what `word` and `cross_call` share, so there is no module cycle (P09).

**What moves.** No manifest, Program or partition count changes. Checker verdicts change as follows:
- **#74 (FP8), owner vLLM FP8:**
  - `ScaledMmFp8Block_v1` recomputes its block scale product `F32Mul(sx[kb], sw[kb])` in every coordinate: 127 copies per (weight block, kb). That is 4 Definitions, 144 groups and 581,040 Calls, with 113.6 G gates computed again.
  - `check_query` / `--word-check` on FP8-block rows now fail by name.
  - The fix is the FP8 Definition's: compute the block's scale products once, in a node the coordinates read, and commit them.
- **The Boolean export's `commitments.json` (#84)** gets the same violation for those Definitions, through `unit_rule`.
- **Pure-wiring Calls** that previously failed with `committed-unread` now pass. None of the 13 rows had one.

**The 13-row check with the fixed rule**
- **Word checker (Q_word_v1 over every group):** 0 violations on 12 rows; #74 `cut` 581,040. Units, gates and committed words are identical to `art:f0c33059…` on all 13. The graphs are `art:c74deac4…` (the graphs handoff, 02:40Z).
- **Cross-Call** (`art:e8b4aada…`, every request Program, both TP ranks; level 3 refined and left unrefined nothing):
  - **#57 Gemma, owner vLLM frontend/Build:**
    - `AddScalarBf16_v1{N=2304,C=1}` (the norm weight + 1 in Gemma's ATen norm chain) is issued at every engine step. Each request Program holds T × 105 copies of the 105 distinct values: 102.6 M gates computed again over its 8 request Programs.
    - The fix is the Build's: issue the `+ 1` once per norm.
  - **0 recomputes** on #11, #23, #39, #60, #67, #68, #70, #73, #74 and #75, and on #101's r19-reference Build (`art:a9be8f7c`).
  - #101's record Build (`ccc21347…`) and #4's request Programs are not in the store, so they weren't run.

**Tests:** these pass:
- `tests/query/test_cross_call.py`: the synthetic duplicate caught, the honest Program passing, operand-subset and gate-level cases, the member check (the FP8 block and a synthetic twice-computed node), and hierarchical support equal to flat;
- `test_word.py` (the pure-wiring cut);
- `tests/pipeline/test_program_graph.py`;
- `tests/lint`;
- `program/test_lint`.

Gate (b) is yours.
