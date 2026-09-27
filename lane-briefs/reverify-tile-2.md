---
cursor:
  subagentId: "bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388"
---

# Lane brief: reverify-tile-2 (cloud lane, relaunch)

**Launch status:** READY (7:10 AM PT, Sep 25). reverify-tile's agent died in the laptop worker's disconnect. Its branch
`lane/reverify-tile` is clean and pushed at f3cdfd5d, which includes main 767115db.

**Launch as:** a Cursor cloud agent in `danielreuter/verity`, base branch `main`. Give it this prompt:

> You are lane `reverify-tile-2`. First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1, then read `$RESEARCH_NOTES/kb/LANE-CONTRACT.md`. Your brief is
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/reverify-tile-2.md`. Run
> `research notes inbox reverify-tile-2` (it includes reverify-tile's unread handoffs), and write your first checkpoint within 10 minutes.

## Goal

Finish what reverify-tile started (read `$RESEARCH_NOTES/lanes/reverify-tile/`, its report and last checkpoint: "fp8-ada /
bf16-hopper benches 87/85 min in, no dump yet"):
1. +shared (v6) / tile dumps become re-verifiable. Add a manifest `set.tile` block written by the bench runner, and a tile
   recomputation in `reverify.commitment_problems` (bindings, roots and cover under the R1 tile rule). A dump without
   `set.tile` still fails closed.
2. Rust `batch` refuses a statement without a proof (done in 0e0d663b; keep its test).
3. The honest shared-local re-productions (fp8-ada 13 and bf16-hopper 25 sub-batches) must pass. Pod `vy-reverify-tile-2`
   was still running those benches at 7:00 AM PT; collect its runs from R2 if they finished, or re-run them on a pod.

## Rules and limits

- Work on `lane/reverify-tile-2`, cut from `lane/reverify-tile` @ f3cdfd5d (see `relaunch-branches-0725.md`). Don't commit to
  `lane/reverify-tile`. No rebases: merge origin/main in if needed.
- Merge origin/main (b874764f or later) before your final tests.
- Tests on a pod: `cargo test --release`, `pytest hashauth_test.py reverify_test.py steps_pin_test.py`, the ligero
  regression list, plus the tile negatives: a remapped tile VU, a wrong `set.tile`, roots not matching the recomputation,
  and a missing `set.tile`.
- When it passes, send the coordinator a merge-ready handoff, and red-team-standard-hash-2 a review request for the tile
  recomputation.
- Terminate `vy-reverify-tile-2` once its runs are preserved (`research data preserved <run>`), and your own pods at the end.
- FINAL: 15:30Z hard. Budget: $10 (pods).
