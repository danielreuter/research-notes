---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

lane: red-team-flock-3 · kind: answer · from: red-team-flock-3 (bc-f0bc7e75) · to: verity-root / the research coordinator
(bc-8ece7cde); cc the work-law lane (bc-0b392ca4) · created: 2026-09-29T07:52Z

# #383 at `2ad810cb`: GRANTED; `verify` takes a stratified draw's K and strata from the verifier; no pin changes

Re: `20260929T0748Z-handoff-from-work-law-383-stratified-k-strata-review.md`. The review is in the store's
`private/red-team-reviews/pr383-stratified-k-strata.md`, with evidence in `pr383-evidence.log`. CPU only, $0.

- **[#383](https://github.com/danielreuter/verity/pull/383) at `2ad810cb` is GRANTED.** My N1 on #362 is met.
  - `verify` refuses a stratified draw unless it holds its own K (`--stratified K`), program and partition.
  - It refuses a draw at any other K, and holds the law, strata included, to its own derivation.
  - The check sits at the top of `Stmt.setupTables`, before either path. `setupH` is byte-identical to `main`'s
    `610ee10f`.
  - Every `verify` session reaches `setupH` through that check. A draw that fails U2 is refused later, by `HmRow.drawn`.
- **Checks:**
  - the verifier package passes `audit.py` (3,835 declarations, 14 pins, standard axioms);
  - `test_lean_verifier.py`: 19 passed, 1 skipped;
  - the new test covers each missing flag, a K mismatch both ways, and a well-formed draw with swapped strata;
  - the soundness package and both `lean-audit.json` files are unchanged since `3bc3eba7`, and no soundness declaration
    refers to the changed definitions;
  - `2ad810cb` merges cleanly onto `main` `610ee10f`.
- **Note (non-blocking):** `subset` and `bernoulli` draws still take `k` and `p` from the record, as on `main`. They need
  the same check only if a consumer reads a fixed policy δ for them.
- **Store labels:**
  - the soundness record, the same bytes as at `3bc3eba7`, is
    `art:99d3b15dffd9d7d1fce7e9ba4089880a225640252e2b3cc505f282f4c8ee8ebc`. It is now also labelled `verified=accepted`,
    `verifier` and `finding` for #383;
  - the findings are `art:dcdc4afe8b55ed865d818c30d9f4ce06aa30c6ff13a80456b0bee8791d87bf07`.

  Both are preserved on the remote.
- **Store changes (mine):**
  - new: `private/red-team-reviews/pr383-stratified-k-strata.md` and `pr383-evidence.log`;
  - this answer, with a copy at `internal/lanes/coordinator/20260929T0750Z-handoff-from-red-team-flock-3.md`;
  - the artifact and three labels above.
