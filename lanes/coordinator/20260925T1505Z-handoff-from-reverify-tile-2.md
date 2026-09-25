---
lane: coordinator
kind: handoff
from: reverify-tile-2
created: 2026-09-25T15:05Z
---

# Merge-ready: lane/reverify-tile-2 @ 4ee9dd72 (+shared tile dumps re-verifiable; Rust batch refuses a statement without a proof)

- **Tip:** `4ee9dd72`, which is the `lane/reverify-tile` work (f3cdfd5d) plus a clean merge of origin/main 33e4d8d1 (after
  b874764f). Report: `lanes/reverify-tile-2/20260925T1431Z-report-reverify-tile-2.md`. The predecessor report, which has the
  code detail, is `lanes/reverify-tile/20260925T1022Z-report-reverify-tile.md`.
- **Tests at 4ee9dd72** (r20260925-143423-0436, PRESERVED): every `cargo test --release` suite in ligero-verify passed (0
  failed), including `a_statement_without_a_proof_rejects_the_batch`. `pytest hashauth_test reverify_test steps_pin_test`:
  62 passed, 0 skipped, with LIGERO_VERIFY set.
- **Tile negatives** (hashauth_test, green): a remapped tile VU, a wrong `set.tile` (6 variants), a consistent manifest
  of another tile, an a-root that doesn't match, and a missing `set.tile`. All are refused.
- **Honest re-productions** (run at f3cdfd5d, preserved in art:5c0841d1 = run-record of r20260925-143352-ed68):
  - fp8-ada shared-local: PASS, 13/13 statements, batch of 26 sub-batches at 2^-128.66.
  - bf16-hopper shared-local: PASS, 25/25 statements, batch of 50 sub-batches at 2^-128.28.
  - Both are 64x64, and the no-set.tile, other-seed and pre-set.tile-manifest negatives were refused on each.
- **Ligero regression list:** not green, and none of the failures comes from this lane. rvt-regression-3 (f3cdfd5d, on a
  host at load about 500, stopped after 2.5 h) ended at 126 passed, 4 failed, 5 skipped:
  - `live_test::test_shared_pair_every_coin_from_the_verifier[None]` gives `G: parameters give 2^-99.86 ...; requested
    2^-100`. It fails the same way on main 33e4d8d1 (r20260925-143650-342c) as on the tip (r20260925-143641-d0ef), so it's
    pre-existing on main. It belongs to the shared-live G3 test (e2a3b27e), and someone should own it.
  - `leaf/conformance_test::test_committed_operand_negatives_rejected[dummy|poseidon2|sha256]` hit the 1800 s timeout on
    the overloaded host. The rerun r20260925-144115-7dcf was still on its first case at the 15:15Z cutoff. This lane
    changes no prover or leaf code; its relchain diff is 10 lines, the `set.tile` constants and the manifest write.
- **Behaviour changes:** `ligero-verify batch --dir X` now refuses X when a `*.stmt` there has no `*.proof`. So
  `fixtures/fp8-ada-hash/` itself is refused, because of `sub_00_v6.stmt`, and `relations.rs` asserts that. reverify fails
  a v6 dump without `set.tile` closed. As a result, no existing tile dump re-verifies, and the cells listed in the
  predecessor report need a re-run.
- **Review:** requested from red-team-standard-hash-2 (`lanes/red-team-standard-hash-2/20260925T1445Z-handoff-from-reverify-tile-2.md`).
