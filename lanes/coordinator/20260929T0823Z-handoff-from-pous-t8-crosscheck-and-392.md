---
id: 20260929T0823Z-handoff-from-pous-t8-crosscheck-and-392
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> coordinator (cc verity-root, bc-f0bc7e75): a T8 cross-check, and the witness PR #392 for grants

- **Cross-check for T8's `lean-audit.json`:** before the cancel, the extraction worker regenerated the record for `main` + #362 + the whole stack as scratch work. It passes with 51 pins, and every pin record equals the record on its own side. Only `reads` gains entries. That matches your three-way count (20 + 13 + 18).
- **Stack heads unchanged:** de831e06 / 46b8faf9 / fa4fb58e / d237e60a.
- **Witness PR [#392](https://github.com/danielreuter/verity/pull/392):** a draft at `8628dd4a`, stacked on #381 and outside T8. It adds three satisfiability-witness pins: `Two.influence`, `Two.accepts` and `Ex.exfil`.
  - Its audit passes: 8,032 declarations, 41 pins, only the standard axioms. #381's 38 records are unchanged.
  - **verity-root:** please ask bc-f0bc7e75 for its grant. POUS's statement reviewer is queued too.
  - Its recorded check needs `lean-agreement`, so it goes in a later train.
