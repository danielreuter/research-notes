---
id: 20260929T1856Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #427's new head is `5550fd7c`; restack #425 on it

Follows `20260929T1848Z-handoff-from-verity-root.md`.

- [#427](https://github.com/danielreuter/verity/pull/427) at **`5550fd7c`** adds `extraction_audit_window_split_of_record_of_le_slack`,
  taken byte for byte from #425's `Audit/WindowCompiled.lean` at `7fd7e0b9` (same statement, same proof). Audit: 9,950
  declarations, 107 pins, standard axioms only; against the granted `dff428ad` the only record change is the new pin.
- Restack #425 on `5550fd7c` and drop both `WindowCompiled` copies; your citations stay unchanged.
- The delta is with bc-f0bc7e75 for a grant, alongside #425.
- #427 stays stacked on #421 until TM lands (merging about 21:30Z, after TB), then rebases onto `main`.
