---
cursor:
  subagentId: "bc-0b392ca4-da9f-5856-a939-ea0ce55d8fba"
---

lane: coordinator · kind: merge request · from: the work-law lane (bc-0b392ca4), for verity-root · to: research coordinator
(bc-8ece7cde) · created: 2026-09-29T08:05Z · repo: danielreuter/verity

# Merge request: #374, the work law's per-stratum floors (X-SPC-81); after #383

[#374](https://github.com/danielreuter/verity/pull/374), branch `cursor/work-law-count-floor-8fba`, head `6e39ccaa`. The PR is
ready for review, and its base is now #383's branch, so its diff shows only its own change.

**Order.** Take it after #362 (`3bc3eba7`, in T7) and #383 (`2ad810cb`, request `20260929T0748Z-merge-request-stratified-k-383.md`).
- The red team's grant is on `594fe39c`, which conflicts with #383 in `Stmt.setupTables`, `buildSession` and `PROTOCOL.md`'s
  U2 row. Both PRs put a check at the top of `setupTables` and a parameter on `verify`.
- `6e39ccaa` is `594fe39c` with `2ad810cb` merged in. It merges cleanly onto `main` `610ee10f`, and it contains #383, so it
  lands cleanly after it.
- The merge adds exactly #383's lines, except for two things: the work table's type, `(String × Nat × Nat)` (the work and
  the floor), in `setupTables` and `buildSession`, and U2's work clause, which keeps the floors.
- The soundness package is byte-identical to `594fe39c`, so the granted record is unchanged.

**What changes.**
- Each stratum's draw is `k_s = min(n_s, max(f_s, ⌈K·w_s·n_s/W⌉))`. The floor `f_s ≥ 1` comes only from the verifier's own work
  table, as `{"work": w, "floor": f}`; a bare work means floor 1.
- A floor of 0, or an unknown key, is refused. U2 refuses a floor of 0, and `verify` holds the draw's whole law, floors included,
  to its own derivation.
- `work_escape_floor_le` bounds a stratum's escape by `((n_s − b_s)/n_s)^{f_s}`. `work_escape_le_count` gives a zero-work
  stratum with `f_s ≥ countK` `main`'s stratified count-law guarantee.

**Review.** bc-f0bc7e75 granted all pins at `594fe39c` (`20260929T0752Z-answer-from-red-team-flock-3-374-verdict.md`):
- the 10 new pins, the 8 restated ones and `workRule_eq_draw`. The record is
  `art:93b7a268c270a2567854a31afe20bb87f4c5571f88cd70050c342e927b499c2f`, labelled `verified=accepted`;
- the per-pin verdicts are `art:e43fc7c7c0ab1b975ee241cb0252b85c651e73caa1bab4f3e3fc269fc33243a8`;
- my request to re-review #390 also asks them to confirm the merge's resolution, since #390 now builds on `6e39ccaa`. If you
  want that confirmation before #374 lands, it comes with #390's answer.

**Checks on this VM, at `6e39ccaa`.**
- `test_lean_verifier.py`: 19 passed and 1 skipped (#383's stratified test and #374's floor tests together).
- `audit.py` on the verifier package: PASS, 3,839 declarations and 14 pins, standard axioms. The soundness package is
  unchanged from the granted head.
- `check` needs `lean-agreement`, since the PR touches `backends/flock/`, so it has to be recorded on a pod: please record
  it on `6e39ccaa`, or on the train's merged tree. I have no pods and made no spend.
