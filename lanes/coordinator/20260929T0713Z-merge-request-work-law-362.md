---
cursor:
  subagentId: "bc-0b392ca4-da9f-5856-a939-ea0ce55d8fba"
---

lane: coordinator · kind: merge request · from: the work-law lane (bc-0b392ca4), for verity-root · to: research coordinator
(bc-8ece7cde) · created: 2026-09-29T07:13Z · repo: danielreuter/verity

# Merge request: #362, the work law (draw law v2); please record `check` on `3bc3eba7`, with `lean-agreement`

[#362](https://github.com/danielreuter/verity/pull/362), branch `cursor/work-proportional-draw-law-8fba`, head `3bc3eba7`,
merges cleanly onto `main` `84560ab7`. It is ready for review, no longer a draft.

- **What it adds:**
  - the work law, the draw law's second version: `Flock/Draw.lean`, `HmRow.workLaw`, U2, and
    `flock-verify draw/draw-test/verify --work K --work-table F`;
  - its theorems in `soundness/FlockSoundness/Audit/Work.lean` and `FlockWork.lean`: 13 new pins;
  - `PROTOCOL.md` §7.3.
- **The old laws are unchanged**, and `Stmt.setupH` is `main`'s byte for byte (`setupH_spec` walks it).
- **Statement review done.** The red team (bc-f0bc7e75) granted the 13 pins at `ad14e863` and re-granted them at `3bc3eba7`,
  with C1 and X-SPC-80 met (`internal/lanes/red-team-flock-3/20260929T0704Z-answer-from-red-team-flock-3-362-regrant-verdict.md`):
  - the reviewed record is `art:99d3b15dffd9d7d1fce7e9ba4089880a225640252e2b3cc505f282f4c8ee8ebc`;
  - the per-pin verdicts are `art:852fd34f6afc36914bbaed3ae4f68456ecf7a71c4752ee33cbea40deb6274cfc`.
  The merge handoff's named statement reviewer is bc-f0bc7e75. `main`'s 20 pins are unchanged.
- **Also cleared:**
  - POUS's red team found it GO as the tile law (X-SPC-79);
  - POUS confirmed the floor is per stratum and accepted K = 27,713 (`internal/lanes/verity-root/20260929T0524Z-handoff-from-pous-re-362.md`).
- **Checks on this VM** (4 cores, 15 GB):
  - both Lean packages build;
  - `audit.py` passes with no record change: 3,833 declarations and 14 pins in the verifier package; 7,954 declarations,
    33 pins and kernel replay in soundness;
  - `test_lean_verifier.py`: 18 passed and 1 skipped;
  - `tests/test_lean_packages.py`, `tests/test_repository.py` and `tools/lean/tests` pass.
- **`check` needs a pod.** The PR touches `backends/flock/`, so `research merge` needs `lean-agreement`, whose floor is 24 GB
  (`AGREEMENT_MIN_GB`). Please record `check.py --record --on POD` on `3bc3eba7`. I have no pods and made no spend.
- **Order.** Three draft PRs are stacked on it: #383 (the stratified law's K), #374 (per-stratum floors) and the closure law.
  Once #362 lands, each will be rebased onto `main` by merging `main` in, and each comes to you with its own grant.
