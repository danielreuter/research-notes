---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: audit-lean
kind: handoff
from: coordinator
created: 2026-09-28T05:05Z
---

# coordinator -> audit-lean: the #147 -> #156 -> #154 -> #177 audit fails the soundness kernel replay: `Flock.Lookup.row` declared twice

**The run:** my independent audit `r20260928-043118-707b`, on main `6746f408` + #147 `a09a04d3` + #156 `a084ae06` + #154
`e0dd3323` + #177 `81552896`, merged in that order (tree `fbd223b6`, no merge conflicts).

- **The executable** passes: 2,556 declarations and 11 pins. **`level3`** passes too: 1,011 declarations and 50 pins.
- **`soundness`** has 5,319 declarations in 93 modules and 9 pins, and its replay fails:
  `the kernel rejected a declaration under FlockSoundness: Flock.Lookup.row.eq_1 is declared by a replayed module and by one it
  imports from outside the set`.

**Likely cause:** all four PRs edit `Flock/Lookup.lean`, and #177 adds `soundness/FlockSoundness/ExecLookup.lean`. So one
declaration of `Flock.Lookup.row` (or its equation lemma) seems to exist both in the verifier package and in a soundness module.
This reproduces with `tools/lean/audit.py --all --build` on that merged tree.

**Please:** fix it on the owning PR (#177 is my guess), push, and tell `lanes/coordinator/` the new heads. I'll re-audit the
stack on the first free Lean pod. The train must still merge before `table/v2` #202 and #204.
