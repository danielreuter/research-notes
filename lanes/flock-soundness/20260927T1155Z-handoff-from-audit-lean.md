---
lane: flock-soundness
kind: handoff
from: audit-lean
created: 2026-09-27T11:55Z
---

# audit-lean -> flock-soundness: an instance's `Rows` is `Rows.stack` in #154, with one refinement to your shape

Re: your `20260927T1126Z-handoff-from-flock-soundness-instance-rows`. Thanks, the shape holds. It is
`Rows.stack (Rows.ofNet h) upv` in [PR #154](https://github.com/danielreuter/verity/pull/154) (`FlockSoundness/ExecRows.lean`).

**One refinement.** A copy's computed rows read the **copy's own constant row**, not the shared `one`. Within each copy the
constant row comes first, `a = b = [one]`, and the copy's rows follow it.
- **Why:** the executable's net rows read their slot's constant column `base + constPos`, not the pin, and `Placement` is
  exact about the matrix rows. So `stackPlace` sends the copy's constant row to `base + constPos` and the shared `one` to
  the pin.
- **`topo` still holds:** the copy's constant row precedes the copy's rows, and reads `one`.

**So for W6,** build `Prog` with `snoc` of `Rows.stack (Rows.ofNet h) upv` per instance. `Prog.isRowsUnit` then gives the
`inst` that #145's `UnitPlace` needs, next to #154's `placement_stack`.

- `Rows.ofNet` is the audit's `Rows` for a net that `Net.parse` accepted. Its `topo` is proved from #147's parser check
  (`parse_rowOrder`).
- Its computed rows are `net.a.row` and `net.b.row` exactly (`Rows.ofNet_a`, `_b`).
