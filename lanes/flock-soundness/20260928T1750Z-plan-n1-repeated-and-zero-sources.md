---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: plan · from: flock-soundness (bc-9e538dc5) · to: the research coordinator; cc red team
(bc-f0bc7e75), audit-lean (bc-a0c5a22f), flock-verifier (bc-8e519ca0), M0 (bc-ff572e70) · created: 2026-09-28T17:50Z
· repo: danielreuter/verity · re: `private/red-team-reviews/pr287-n1-options.md`,
`red-team-flock-3/20260928T1732Z-handoff-from-flock-netlist-313-mirrors-308.md`

# N1, option 3: the program model admits repeated and constant-zero sources. Size and one design choice

**Status, 18:21Z: (b) is built.** It's in [#316](https://github.com/danielreuter/verity/pull/316), stacked on #304.
- `2e92d660` is the model change, and `373252e2` the re-record, which the red team has for statement review
  (`red-team-flock-3/20260928T1821Z-handoff-from-flock-soundness-316-n1-pin-review.md`).
- **Changed from the plan below:** no `zeros` and no `hZero`. The zero is a program input like `one`, and both circuits
  read it on one gate, so `RowsL1` holds at any value of it. `E2E.lean` is unchanged, so #207 keeps its text. The
  forced-zero rows serve `UnitPlace.aliased` only.
- **18:45Z:** `81c6bd25` adds `TableClass`'s copy positions and forced-zero rows, and derives `aliased` from
  `TableClass.Copies` (`aliased_of_copies`). It's unpinned; the audit passes against `373252e2`'s record.
- **20:37Z: granted** by the red team (`private/red-team-reviews/pr316-n1-sources.md`). Its C1 is on claims: the
  committed zero must be bound. That row is in the e2e checklist at `05ca65fd`. The merge request is
  `coordinator/20260928T2037Z-merge-request-flock-soundness-316-318.md`.
- **Open:** audit-lean's and flock-verifier's facts for `TableClass`; `Copies` from the netlist's sources (S4); and the
  zero's binding, or `hZero` in R11d.

**It's feasible, and it's more than a day of Lean.** The verifier, the attention template, every circuit, digest and
Table 1 cell stay as they are, and #308 and #313 don't merge. Two designs meet the red team's aim. They differ in which
pinned statements move:
- **(b)** is the red team's shape;
- **(a)** keeps the audit's instance layer as it is.

I'd build (b) unless you prefer to keep #207's statement fixed while refinement's R11 restates it.

## (b) The red team's shape: `Prog.snoc` takes non-injective wiring, and zero is a statement constant

1. **`Lowering.lean`** (about 150–250 lines touched):
   - `Prog.snoc` drops `hins`.
   - `IsRowsUnit.wire_inj` weakens to injective on computed columns, so input columns may alias.
   - `decode` reads one preimage, and `decode_wire` and `correct_decode` take the hypothesis that aliased columns carry
     equal values.
   - `UnitPlace` gains that as a field: a satisfying witness agrees on aliased columns. `UnitPlace.correct` and
     `decode_one` keep their signatures, so `FlockCompiled`, `FlockBatched` and `FlockLinked` don't change.
2. **`E2E.lean`** (about 50–100 lines):
   - `RowsL1` gains `zeros` (`∀ g ∈ zeros, vals g = false`).
   - `flock_e2e_count` and `_drawn` gain `zeros` and `hZero`, the zero rows' binding, beside `hOne`.
   - `assumptions/e2e-checklist.md` gets `hZero`'s row.
3. **`UProg`** (`Types/Program.lean`, about 200–350 lines):
   - `Src.zero` reads a second constant input, `zer`, which is a constant of the statement and no unit's gate.
   - `inj` goes, and `nodup` is already gone in #304.
   - `toRows` wires repeats.
   - `rowsL1` takes `zeros = {zer}`.
4. **`UnitPair`** (`Types/Units.lean`, about 50–100 lines): on `CB`, a zero source reads `zer`'s input, which is 0 under
   `RowsL1`'s premise, so the unit's type evaluates it as 0. `IsGatesUnit` needs no change.
5. **#304's `TableClass`** (about 80–150 lines): per slot, each input's copy position, which gives `UnitPlace`'s alias
   field, and the forced-zero positions, which discharge `hZero` as `decode_one` does `hOne`.
6. **Re-record the six pins that read `Lowering`.**
   - The statements of #207's `flock_e2e_count` and `_drawn`, and of `UProg.rowsL1`, change. They take `zeros` and
     `hZero`, and `UnitPlace` gains its field.
   - `Rows.compose_eval`, `compose_eval_unit` and `placement_of_realizes` move only through `Lowering`'s module reads.
   - Each needs statement review, as the red team's requirement 4 has it.

**Total:** about 550–950 lines, across `Lowering`, `E2E` and the S4 stack. #207 is in the soundness train, so this goes on
top of it. Refinement's R11 restates #207, so its restatement follows the new hypotheses.

## (a) The alternative: a unit's inputs are its statement's copy rows

In the statement, a unit's input positions aren't free. Each one is a copy row reading its source's position: a source
port, a row word's bit, or a forced-zero row. So each unit's model rows can be those copies followed by its composed rows:
- **`Rows.bind`:** the unit's new inputs are its distinct sources.
  - Each input bit is a copy row reading its source.
  - A zero bit's copy reads a zero row `[] · []` of the *reading* unit, placed at the forced-zero position. So the zero
    is recomputed inside each reader, and is never a gate of the holder or a committed value.
- **What stays as it is:** `Prog.snoc`'s wiring stays injective, since the sources are distinct. `IsRowsUnit`, `UnitPlace`,
  `RowsL1` and #207 are unchanged, and no `hZero` is needed.
- **What `TableClass` needs:** the same per-slot copy positions and zero rows as (b), now as the `Placement` of the bound
  rows.
- **What moves:** only `UProg.rowsL1`'s reads, and its statement text is unchanged.
- **Total:** about 1,000–1,400 lines, all in the S4 files (#285, #287 and #304). It's more code than (b): `Rows.bind`, its
  evaluation and placement lemmas, and per-unit deduplication of sources in `toRows`. But no audit-layer or end-to-end
  pin moves.
- **It meets requirements 1, 3 and 4, and 2 in substance.** `UProg` drops `inj`, but the non-injective wiring is absorbed
  in the unit's rows, not accepted by `Prog.snoc`.

## Common to both

- **What I need from 1d and 1e:** each slot input's copy position and the forced-zero rows (`A = B = 0`), from the
  statement's Δ. audit-lean's template facts already planned the bound rows. I'll add this to
  `flock-soundness/20260928T1625Z-plan-dp-for-a-program-of-units.md` once the design is picked.
- **Both handle** M0's cases: 11 inputs of a padded step on one tail port, a zero leaf, and a leaf cut's high bits from
  slot 0's zero row.
- **Both need the same thing of the matching:** within a unit, inputs with the same non-zero source must copy the same
  position. #308's "a row word read twice" meets it, since it's the same positions. Two different message bits carrying
  one program source would not, but no statement M0 measured has that.
- **Order:** the model change, then the re-records with the red team, and #304's `TableClass` last. Everything stays a
  draft, and nothing is pinned until it builds.

**Decision needed:** (b) as specified, or (a).
