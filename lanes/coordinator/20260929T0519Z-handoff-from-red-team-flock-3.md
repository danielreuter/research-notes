---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

lane: red-team-flock-3 · kind: answer · from: red-team-flock-3 (bc-f0bc7e75) · to: verity-root / the research coordinator
(bc-8ece7cde); cc the work-law lane (bc-0b392ca4) · created: 2026-09-29T05:19Z

# #362 (the work draw law) at `ad14e863`: all 13 new pins GRANTED; one condition on the executable

This is a statement review of [#362](https://github.com/danielreuter/verity/pull/362) at its exact head `ad14e863`. The
review is in the store's `private/red-team-reviews/pr362-work-law.md`, with evidence in `pr362-evidence.log`. CPU only,
$0.

- **All 13 new pins are GRANTED.** They say what the PR claims, and none is vacuous or weaker than its name:
  - the work bound ((W − W_B)/W)^K, at both audit layers;
  - the floor (≥ 1 per non-empty stratum, unconditional), with whole-stratum catches at both layers;
  - Σ k_s ≤ K + m;
  - K = 27,713 meets 2^-40 at ε = 0.1%, and 27,712 doesn't under this bound;
  - the closure seam `escape_widen_le`;
  - the `rfl` bridge `Flock.Draw.workK = Law.workRule`, which covers the rule only.
- **The existing 19 pins are unchanged.**
- **Checks at `ad14e863`:** both packages build. `#print axioms` gives the standard axioms (`workRule_eq_draw` uses
  none). `audit.py` passes on the verifier package (3,503 declarations, 13 pins) and on the soundness package with
  kernel replay (6,152 declarations, 32 pins).
- **C1, on the executable, before any claim cites the work bound.** `Stmt.setupH` holds a work draw to the verifier's own
  work table only when partition, program and table are all given. Without `--work-table`, U2 accepts the draw's stated
  `work`, which sets every k_s. Make `verify` refuse a work draw unless it holds its own table, program and partition,
  or report whether the law was its own derivation.
- **Store labels:**
  - the reviewed record, the soundness `lean-audit.json` at `ad14e863`, is
    `art:63602bf7dcc2202bbd79cd7040dae4afdfa8db93aac29dfa562d88d03d550208`, labelled `verified=accepted`, `verifier` and
    `finding`;
  - the per-pin verdicts are
    `art:f791370e6a58355f17e02db44e5e0be4b196e868bbc3a643c259ae6969ccfd3f` (`redteam-findings/v1`, 13 GRANT and C1).

  Both are preserved on the remote.
- **Store changes (mine):**
  - new: `private/red-team-reviews/pr362-work-law.md` and `pr362-evidence.log`;
  - this answer, with a copy at `internal/lanes/coordinator/20260929T0519Z-handoff-from-red-team-flock-3.md`;
  - the two evidence-store artifacts and three labels above.
