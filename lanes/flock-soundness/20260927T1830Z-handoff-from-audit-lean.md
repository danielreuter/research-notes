---
lane: flock-soundness
kind: handoff
from: audit-lean
created: 2026-09-27T18:30Z
---

# audit-lean -> flock-soundness: the placement is proved from `Stmt.setupH`; W6 is the one piece on your side

[PR #177](https://github.com/danielreuter/verity/pull/177) (`cursor/audit-placement-exec-f568`) is stacked on #154, with
#156 merged in. It proves #144's `Placement` from the executable's accept step (`placement_of_setupH`).
`unitPlace_of_setupH` builds the `UnitPlace` that `loweringSoundB_of_place` takes.

## What `unitPlace_of_setupH` needs from the circuit side (W6)

- **`inst : P.IsRowsUnit u ((unitRows st L.unit_parsed).stack st.c.upv)`**, where:
  - `unitRows st h := Rows.ofNet (Classical.choose_spec h)` is the unit net's rows, as your 11:26Z answer agreed;
  - `.stack upv` is #154's `Rows.stack`.
- **If `Prog.circuit` is built with one `snoc` per instance with these rows,** `Prog.isRowsUnit` gives `inst` directly.
- **The rows depend only on the parsed unit net `st.c.unit`,** through `Rows.ofNet`. So the registration's program has
  to use the same net: the pinned file's `unit` block.

## What it rests on

- The model statement is `Layout.model`: the verifier's `m`, `k_log` and pin, `A₀ := placedA st`, `B₀ := placedB st`,
  and the public regions as a parameter (`regs`).
- The regions translation is not needed for `Placement`. It will matter where the model's `Satisfies` meets the fold
  theorem (L3-A).
