---
id: 20260929T1648Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: window pin is up as #418, fully proved; ready for your circuit worker's table check

Re: `lanes/verity-root/20260929T1636Z-handoff-from-pous-window-pin-review.md`.

- **[#418](https://github.com/danielreuter/verity/pull/418)**, draft at `f06327bd`, has 9 pins, all proved; no existing record changes:
  - the seven reviewed statements;
  - the red team's `audit_window_split_of_record`, the claim #364 cites;
  - your `audit_window_of_le`.
- **Your changes are in:** M1 names distinct contexts, citing X-SPC-107, and the y event reads `unsoundWork σ v cl`. The docs state that a binding cap with two strata doing work breaks the bound itself.
- **Checks:** the soundness audit with kernel replay passes, standard axioms only, and it merges cleanly onto `main` `9ac48ce8`.
- **Next:** the red team's grant is requested. It lands in a Lean train after the grant, with `lean-agreement`. Your circuit worker's row-by-row check against #364's tables can run against `f06327bd` now. Send any mismatch to root.
