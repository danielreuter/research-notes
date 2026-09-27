---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T02:45Z

# Merge request: PR #96 @ e213a324 (router-softmax tap + TP vocabulary range, opt-in `ROUTER_TAP` / `VOCAB_TAP`): APPROVE

The lane's handoffs are `vllm-coordinator/20260927T0136Z-handoff-from-vllm-rf-moetap.md` (the GPU evidence) and
`…T0225Z…` (the merge with main).

- **Order:** #86, #90, #92 and #95 are all on main. `e213a324` is a real two-parent merge (`c574c4a5` + main `fa662029`),
  and it merges cleanly into current main `c822ca7a` (which includes PR #101).
- **Conflict resolution:** the guarded max stays its own parameter beside `taps`, and its header code is untouched. The
  router and vocab sources, `registry/moe.py`, the tap slots and the drivers are unchanged by the merge, so the GPU
  records stand.
- **GPU evidence (root's condition: the kernel's max is `fmaxf` and the GPU's NaN is `0x7FFFFFFF`):**
  - router-tap exactness `r20260927-011454-7498`, `ok`: 4 × 1,024 rows (24 edge rows included), with 0 tap-vs-IR word
    mismatches and 0 output mismatches;
  - outputs bit-identical to the installed op and to the tap-off build;
  - the live check on OLMoE-shape and Qwen3-MoE-shape engines: 0 row mismatches, tokens equal.
  - The #86 comparison shows #86's statement differs on 20 of the 96 edge-row sets (all NaN, a NaN in a thread's last
    column, subnormals). The `0x7FFFFFFF` mapping is kept, per root.
- **Other records:** TP2 vocabulary range `r20260927-011644-9037`, `ok`; partition report `r20260927-005720-ee97`, 0
  recomputes, committed words = tap words.
- **Default path:** with every flag off, main and merged give a byte-identical #101 manifest (`368283ad…`, 7,043
  identities), and the `--guarded-max` path is byte-identical too.
  - The stored #101 Build is the one whose manifest is `368283ad…`. The newer pod Build (`90f81868…`) has no stored
    artifact, and reproducing it needs a GPU.
  - Because this is an A/B on the same inputs and the merge only touches plumbing, I accept it as evidence that the
    default path is unchanged.
- **Tests:** my jdiff of main `c822ca7a` against main + #96 over `tests/query`, `pipeline`, `properties`, `acquire`,
  `commit`, `program`, `engine` and the lints:
  - 2,581 tests; 62 new tests pass; one new collection skip (`test_vocab_range_source`, needs torch; it passed in the
    lane's pod gate (b));
  - one new failure, `test_row::test_the_expiry_path_still_kills_the_forked_worker` (`int('')`). It passes 3/3 on both
    trees in isolation, and #96 doesn't touch `row.py` or `test_row.py`, so it's a load race.
  - The lane's pod gate (b), base 5b0835d4: jdiff rc 0, 65 new tests.
- **Spend:** about $6.06 of the lane's $8. Its pods are terminated.
