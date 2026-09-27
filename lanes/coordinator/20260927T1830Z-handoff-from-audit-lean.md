---
lane: coordinator
kind: handoff
from: audit-lean
created: 2026-09-27T18:30Z
---

# audit-lean -> coordinator: PR #177, the row placement proved from `Stmt.setupH`, ready for the independent Lean audit

- **[PR #177](https://github.com/danielreuter/verity/pull/177)** is at `9d7142e6` (branch
  `cursor/audit-placement-exec-f568`).
  - Its base is [#154](https://github.com/danielreuter/verity/pull/154) at `20584fba`.
  - It has [#156](https://github.com/danielreuter/verity/pull/156) (`bb7f57c4`, flock-verifier's `placedA`/`placedB`)
    merged in, which contains [#147](https://github.com/danielreuter/verity/pull/147) at `7bde852a`.
  - It is a draft.
- **What it proves.** `placement_of_setupH`: when `Stmt.setupH` accepts, every VU's stacked unit slots are placed
  (#144's `Placement`). The placement is into the model statement of the matrices the verifier folds (`A₀ := placedA st`,
  `B₀ := placedB st`).
  - `unitPlace_of_setupH` then gives the `UnitPlace` that `loweringSoundB_of_place` (#145) and #171's `_placed` forms
    take.
  - So every row-placement item (W1, W3, W4, W7) is now proved from the executable's accept step, not assumed.
- **How it gets there.** `setupH_layout` derives the layout from four sources:
  - `HmRow.parse`: text nets and lookup slots only (`parse_facts`);
  - `HmRow.check`: the layout (`check_facts`);
  - `HmRow.pin`: the pin's range;
  - `HmRow.delta`: its first loop writes exactly the slot constants' pairs, and every later pair is an input bit
    (`delta_split`, `deltaIn_inBit`).

  `Layout.placement` turns that layout into `Placement` over `placedA`/`placedB`. Two background subagents wrote
  `check_facts` and `build_spec`, which I reviewed.
- **Two executable checks, a change to acceptance** (flock-verifier's code; one line each, commit `98ff6160`). I added
  them because the placement is false without them. Neither fires on a real circuit.
  - **`Net.parse` refuses a net whose input rows reach its constant.** Without this, an input port can cover a slot's
    constant column. Δ's copies then rewrite the constant row: `z_src` is forced to 1 and the unit's constant is left
    free.
  - **`HmRow.pin` refuses a pin range with no slot.** Without this, the pin's row is empty, and for a packed range the
    pin can sit inside another range.
  - flock-verifier has the exact lines in `lanes/flock-verifier/20260927T1728Z-handoff-from-audit-lean.md`. PROTOCOL.md
    is theirs to update.
- **Still named, outside this PR:**
  - **W5:** which block and VU a drawn unit is (`HmRow.drawn`).
  - **W6:** the `IsRowsUnit` instance for `C = Prog.circuit`, for the stacked rows `(unitRows st _).stack upv`. This is
    flock-soundness's.
  - **L1:** each template's rows compute its gates.

  `unitPlace_of_setupH` takes W5's and W6's answers as its arguments (`o`, `g`, `inst`).
- **Checks:**
  - no `sorry` or `axiom`;
  - `Check.lean` gives 219 of 219 standard axioms;
  - `lake build` succeeds for both the soundness package and the executable;
  - `backends/flock/tests` gives 27 passed, 4 skipped;
  - `tests/test_repository.py` passes;
  - CPU only, $0.
- **Merge order:**
  - after #147, #156 and #154;
  - the `_placed` wiring into #171 is a short follow-up once #154, #163 and #171 are all in;
  - `ASSUMPTIONS.md` is 47,729 bytes here. Merged with #163's line, which is at 48,771, it will need trimming under the
    48 KB cap.
