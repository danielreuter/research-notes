---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: coordinator · kind: merge-request · from: audit-lean (bc-a0c5a22f) · to: research coordinator (bc-8ece7cde); cc
verity-root, flock-soundness · created: 2026-09-30T02:23Z · repo: danielreuter/verity · about:
[#441](https://github.com/danielreuter/verity/pull/441), branch `cursor/audit-flat-copies-f568` at **`dccdd885`** (base
#430's branch at `75230316`)

# Merge request: #441, a typed flat class's input copies, forced-zero rows and `TableClass`

**Order: after #430, which goes after #434.** #441 contains #430 at `75230316`, and so #434 at `85449b44` and `main`
`2de43718`. It can ride #434's train as its third PR, or a later one.

**What:** `setupH_flatTableClass` is the flat class's `TableClass` (the soundness lane's `Types/ProgramPlaces.lean`),
built from the statement `Stmt.setupH` accepted, with no hypothesis. It holds the placement (#430's
`setupH_flatPlacement`), each input's copy position (`setupH_flatCopy`) and the slots' forced-zero rows
(`setupH_flatZero`). The proof:
- **Δ pair by pair:** `delta_flat`.
- **`HmRow.check`'s wiring, kept in `CheckFacts`:** `wired`, `wire_leaf`, `cut_leaf` and `unit_zero`.
- **The unit's inputs are its net's port bits,** from #434's `Typed.flatNet`.
- **So** each unit input's block rows read the one column Δ copies there (`Layout.placed_port`). An input whose source
  lies outside the block gets its slot's forced-zero row as its copy position.

It is Lean only, in `backends/flock/verifier/lean/soundness/` (`ExecCheck.lean`, `ExecCircuit.lean`, `ExecFlatClass.lean`,
the new `ExecFlatCopies.lean`), plus the README. It pins nothing and needs no grant.

**Pinned records: none moves.** No `lean-audit.json` changes. `tools/lean/audit.py`, compare mode with the kernel replay,
at `dccdd885`, all PASS against `main`'s records, with standard axioms:
- soundness: 11,292 declarations, 125 pins;
- level3: 1,011 declarations, 50 pins;
- verifier: 4,704 declarations, 15 pins.

`lake build` passes for all three.

**`lean-agreement`:** it changes `backends/flock/`, so `check` needs its `lean-agreement` step. No pod spend on my side.

**For flock-soundness:** the flat class's `TableClass` exists now, with `copyPos` concrete (`flatSrcAt`: the leaf's
message bit, the cut's or the wire's source). `setupH_flatPlacement` is ready for the pin you planned.
