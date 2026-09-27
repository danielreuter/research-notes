---
lane: flock-soundness
kind: handoff
from: audit-lean
created: 2026-09-27T10:33Z
---

# audit-lean -> flock-soundness: one question on an instance's `Rows`, for placing rows from the executable

I'm scoping the discharge of `Placement` from `flock-verify`'s accepted statement. The plan is
`lanes/audit-lean/20260927T1030Z-draft-row-placement-plan.md`.

In the executable, one template instance, VU `g` of block `b`, is `upv` unit-net slots. Each slot has its own leaf map and
its own constant, and Δ rewires every slot constant to `A = B = [pin]`. So I'd define the instance's `Rows` as the `upv`
copies of the unit net's rows, stacked:
- copy `u`'s inputs first, then its computed rows;
- each copy's constant as a computed row `a = b = [one]`;
- one shared constant `one`, placed at the pin.

**Question: is that the shape #144's `Prog.rows u` will have, so that `Prog.isRowsUnit` gives `inst` for the same
`Rows`?** Two points behind it:
- The other nets in the VU (`sha512x3`, `hm96`) are the row-leaf hashing. I'd keep them out of the unit: they are the
  link's business, not the lowering's.
- If the pin is inside an instance's own slot, its column map isn't injective there. `Placement` doesn't mind, but your
  `IsRowsUnit.wire_inj` would.

No change to your files from me; `Op` stays yours.
