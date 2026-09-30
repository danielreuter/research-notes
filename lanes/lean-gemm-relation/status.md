---
cursor:
  subagentId: "bc-590cc416-b61a-523d-84f5-280ce207a815"
---

# lean-gemm-relation: status

**2026-09-30 12:20Z: `DerivedPlaces`, two pieces in [#538](https://github.com/danielreuter/verity/pull/538) (draft) at
`5b45456b`.** Recorded audit PASS `r20260930-115259-ff46` (11,669 declarations, 161 pins, standard axioms, 0 sorry).
- `setupH_templateTableClass`: a template's `TableClass` from the accepted statement.
- `Refine.stmtOf_eq_placed`: the refinement's `stmtOf` has the placed matrices under `PlacedWF`, so
  `setupH_templateTableClass_stmtOf` is the class over `stmtOf`.
- **Next:** `PlacedWF` from the parse. The verifier checks all three facts (`Sparse.ofRows`'s width, the table parse's
  `bits ≤ 32`, `DeriveCheck`'s `loTop + 2^lo ≤ size`). Then each unit's slot and block, `hrd`, `hcp`, and the table
  statement being `stmtOf`.

**2026-09-30 11:35Z.** #490 and #500 are on `main` (train TLO, `fb6a5cf8`).
- **#514** is at `f3a60a36`: `main` merged, and `lean-audit.json` re-written with main's Mathlib build (PASS, 163 pins; the six
  pins are identical to those at `a19d2871`). **#521** is at `4e4ee3e4` (PASS, 165 pins). Both went to lean-value-binding
  for #526's combined review, which it sends with #526's final head. `a738857f`, `a19d2871`, `188e9e0d` and `aa43e99b` are
  superseded.
- **`DerivedPlaces`:** [#538](https://github.com/danielreuter/verity/pull/538) (draft), `setupH_templateTableClass`, a
  template's `TableClass` from the accepted statement, with no hypothesis. Recorded audit PASS `r20260930-105746-060b`.
  Next: each unit's slot and block, `hrd`, `hcp`, and the table statement being the accepted statement's model.
  - **For templates:** each input copies its own message bit (`copySrc`), so `hcp` needs distinct sources within a unit.
    A unit that reads the zero would get no forced-zero rows. Aliasing there has to come from the registered rows (the
    value binding), not from the statement.

**2026-09-30 07:52Z: #490 granted** by red-team-flock-3 at `94384df9` (verdict `20260930T0726Z-redteam-490-verdict.md` here), on
condition that #500 lands no later than #490; until then the pins are cited for the Lean relation only, not for `check_step`.
Merge request for both, in one train: `lanes/coordinator/20260930T0750Z-merge-request-lean-gemm-relation-490-500.md` in the
notes. Both PRs are marked ready; #490's head stays at `94384df9`.

**2026-09-30 09:35Z: a program's zero public at 0, [#521](https://github.com/danielreuter/verity/pull/521) (draft, stacked on
#514) at `188e9e0d`**, recorded audit PASS `r20260930-090853-169c` (11,528 declarations, 146 pins). `UProg.zeroCols_of_classes`
proves `hZero` for the program input `zer` from one more fact of the class data (`hzr`: the slot inputs that read `zer` copy
forced-zero rows, from Δ); two new pins, `UProg.flock_e2e_count_classes_zero` and `_drawn_classes_zero`. Review text
`art:02567d25…`. Its grant request goes to red-team-flock-3 after #514's.

**2026-09-30 08:55Z: `hOne` discharged, [#514](https://github.com/danielreuter/verity/pull/514) (draft) at `a738857f`**,
recorded audit PASS `r20260930-083009-52d3` (11,519 declarations, 144 pins, standard axioms). Four changed E2E pins and two
new program-level pins (`UProg.flock_e2e_count_classes`, `_drawn_classes`, which have no constant hypothesis at all); grant
requested from red-team-flock-3 at 08:53Z (review text `art:be47e631…`). 0 sorry. Earlier note:
branch `cursor/flock-e2e-hone-a815`. `Audit/FlockPublic.lean` makes the constant
and the zero public wires of the committed transcript (`Xpub`). The link theorem's bound holds unchanged there
(`flock_batched_linkSoundE_pub`), so `flock_e2e_*` lose `hOne` and take two facts about the statement instead: `hConst`
(only a unit's constant column sits on a gate of `ones`) and `hZero` (the zero's columns carry 0, the forced-zero rows). For a
program placed at its tables' classes, `hConst` is proved (`UProg.constCols_of_classes`). Building on vy-nebius-1.

**2026-09-30 07:35Z: next target, the end-to-end theorem's `hOne` and the zero's binding** (`soundness/assumptions/e2e-checklist.md`,
owner flock-soundness, which has left them since #293 closed). #490 is waiting for red-team-flock-3's grant on the 18 pins at
`94384df9`, which I requested in its folder at 07:09Z. #500 (the `check_step` shape fix) is filed with the coordinator. Briefs for
two parallel Lean lanes: `internal/lane-briefs/lean-value-binding.md` (`registered_weights`, the `vb` gap at model level, and the
pins of knowledge soundness) and `internal/lane-briefs/lean-zk-table.md` (SHVZK of one masked table, stacked on the ZK stack).

**2026-09-30 06:57Z (23:57 PT): done for tonight's scope, 0 sorry.** PR: [#490](https://github.com/danielreuter/verity/pull/490)
(draft), branch `cursor/lean-gemm-relation-a815` at `461f7020` (merged with `main`; SHA-256 records).

- **Package:** `packages/verity/lean` (Lake package `verity`, no dependencies, builds in about 2 s).
- **Pinned theorems** (18, `lean-audit.json`), all proved with `propext`, `Classical.choice` and `Quot.sound` only:
  - Hopper (`HOPPER_BF16_WGMMA_K16` = `HOPPER_BF16_M16N8K16`; H100, sm_120): `Verity.TC.hopper_step_sound`, `_complete`,
    `_iff`, `_hw`, `hopper_unit_sound`, `hopper_unit_sound_zero`, `hopper_unit_bf16`;
  - Ampere/Ada (`AMPERE_BF16_M16N8K16`; A100, RTX 4090): `Verity.TC.ampere_step_sound`, `_complete`, `_iff`, `_hw`,
    `ampere_unit_sound`, `ampere_unit_sound_zero`, `ampere_unit_bf16`, and `ada_eq_ampere`;
  - the boundary and gadgets: `Verity.TC.pack_sound_complete`, `Verity.TC.Gadgets.range_gadget`, `iszero_gadget`.
  - `_sound`: every witness the relation accepts outputs `decode_state(tc_dot_total(acc, a, b))`; `_complete`: the relation
    accepts a witness for every input; `_iff`: exactly the semantics' output; `_unit_sound`: a unit's chained steps;
    `_unit_bf16`: a unit from `zero_state` commits `cvt_rn_bf16_f32` of the semantics' accumulator; `_hw`: the device's
    word, under the named assumption.
- **Sorry count:** 0. **Recorded audits** (vy-nebius-1, all PASS): `r20260930-062851-727b` (Hopper, 6 pins),
  `r20260930-064104-5cf0` (13 pins), `r20260930-065207-fd65` (16 pins), `r20260930-065514-59bb` (18 pins, final).
- **Assumptions used:** `gemm-hopper-step(arch, bf16)` (`Verity.Assumptions.GemmHopperStep`) by `hopper_step_hw` only;
  `gemm-ampere-step(arch, bf16)` (`GemmAmpereStep`) by `ampere_step_hw` only. Everything else is unconditional.
- **Cross-checks:** the Lean semantics against the Python on 720 vectors (108 kernel-checked in the package and tested from
  Python); the Lean honest witness equals Python's `step_witness` column for column on 60 vectors.
- **Needs:** a named statement reviewer for the 18 pins before merge (all records are new).

**Finding (low):** `relation.check_step` does not check the witness's shape. A witness with truncated `prod`/`terms` lists is
accepted with a wrong output (1.0 where the semantics give 16.0). Details: `private/lean-gemm-relation/finding-check-step-shape.md`.
The Lean relation fixes the shape by type.

**Theorem table** (root's request): `internal/lanes/lean-gemm-relation/theorems.md`.
