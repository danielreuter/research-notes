---
id: proofs/20261002T0838Z-finding-e2e-pp-statement-review
campaign: e2e-guarantees
lane: proofs
kind: finding
status: final
repo: danielreuter/verity
origin: cursor/e2e-const-95d4@f5a7d2b12
---

# Statement review: e2e ProgPlaces, aliasing, hConst, hZero (49 new pins), APPROVE

Reviewer: proofs (bc-8416bc72), 1:50 AM PDT Oct 2. Head `f5a7d2b12` (`cursor/e2e-const-95d4`). It merges e2e-placed
`abb8217d1`, e2e-aliased `86a9bff6d` and e2e-zero `b3d224e86`.

## What I compared

- `lean-audit.json` at the head against main `b8c9dd478`: 214 pins become 263. The 49 new ones are Placed 9, Aliased 13,
  Const 11 and Zero 16. No pin is removed or changed. Every read record keeps its digest and definitions; only the read-by
  lists grow.
- Each worker's `audit.py --update` output (in `internal/proofs/e2e/<name>.md`).
- The `ExecCircuit.lean` edit: `parse_facts_nets` strengthens the old body, and `parse_facts_pre` keeps its statement.

## The statements that feed the headline

- `Discharge.Placed.Sites.progPlaces_keyProg hU hparse outs : ProgPlaces (keyProg c hU n) outs plan tab`. Its parts are
  the pinned `Accepted.placement`, `Accepted.rows_eq`, `Sites.placed`, `Sites.rowsOf_keyProg`, `Sites.aliased_keyProg`,
  `Sites.progPlaces_keyProg_inst` (by `rfl`) and `keyProg_wire_key`.
- `Discharge.Aliased.setupH_aliased_of_key`: for any instance whose shared gates join only inputs with one `srcKey`, setupH
  gives `Layout.Aliased`. It rests on `copyPos_block` and `zeroPos_block`.
- `Discharge.Const.constCols_keyProg`: ones = {the program's constant gate}. Its only inputs are `hU`, `si` and `hparse`.
- `Discharge.Zero.zeroCols_keyProg`: zeros = {the program's zero gate}, from the same inputs. `accepted_zero_block` is the
  real content: a forced-zero input column of an accepted VU is 0 in every satisfying witness.

## Scope (what the statements don't say)

1. W6 is definitional on the untyped path. The headline bounds wrong units of the circuit's own rows. Nothing verifies
   that the unit net lowers its template's Definition.
2. `Sites.vu` and `Sites.o` are free, and every theorem here holds at any choice. Binding them to the drawn unit's real
   site is e2e-layout's site fact (`instOf … = some r`), and the integrator has to supply it.
3. `hparse` takes one circuit `c` for every drawn table. That's right for one circuit file per session. A session whose
   tables carry different circuits needs one `c` per table.
4. `aliased` is relative to what Δ copies. What the copied columns hold is e2e-layout's (`decode_row`, the region pins).
5. Tail stages of `tc_units` templates sit outside every unit's rows.

None of these is a defect in the statements. They are the boundary the integration has to close (2, 4) or state as scope
(1, 3, 5).
