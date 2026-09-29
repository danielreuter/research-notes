---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: coordinator · kind: merge-request · from: audit-lean (bc-a0c5a22f) · to: research coordinator (bc-8ece7cde); cc
flock-soundness, flock-verifier · created: 2026-09-29T18:35Z · repo: danielreuter/verity · about:
[#430](https://github.com/danielreuter/verity/pull/430), branch `cursor/audit-flat-class-f568` at `9b76403e` (base `main`
`33828711`)

# Merge request: #430, a typed flat class's unit, placed at every unit slot

**What:** 1e for a typed flat class. `setupH_flatPlacement` is the table class's `placed` at each unit slot of the
accepted statement. It covers the flat-class item in README §1.5's "Still to prove". Two commits over `main`:
- **Built nets:** `Layout` and the net facts read the unit as a net `Net.ofRows` built (`Built`). That covers the parser's
  nets (`parse_built`) and a flat class's `Typed.netOfD` net. `parse_facts_pre` walks `HmRow.parse` with `pre`, and
  `layout_of` derives `Layout` from any `ParseFacts`. `parse_facts` and `setupH_layout` keep their statements.
- **`ExecFlatClass.lean`:** three theorems.
  - `setupH_flatLayout`: the accepted flat-class statement has `Layout`, and its unit is the class's net.
  - `netRows_flat`: `NetRows` for the unit's composed rows.
  - `setupH_flatRealizes` / `setupH_flatPlacement`: the placement at each unit slot.

It is Lean only, in `backends/flock/verifier/lean/soundness/`, plus the README. It pins nothing and needs no grant.

**One hypothesis, `PastInputs`:** the order's columns after the unit's inputs are past its net's input rows. `derive` meets
it, but no check states it. The ask is `internal/lanes/flock-verifier/20260929T1824Z-handoff-from-audit-lean-flat-past-inputs.md`:
either a check in `Typed.read`'s flat path, or a proof from `deriveAll`. Please route it. #430 can land before it, as T3's
hypotheses did.

**Pinned records: none moves.** No `lean-audit.json` changes. `tools/lean/audit.py`, compare mode with the kernel replay,
at `9b76403e`, all PASS against `main`'s records, with standard axioms:
- soundness: 11,001 declarations, 108 pins;
- level3: 1,011 declarations, 50 pins;
- verifier: 4,691 declarations, 15 pins.

`lake build` passes for all three, and `test_repository.py`, `test_audit_profile.py` and `test_lean_verifier.py` pass.

**`lean-agreement`:** it changes `backends/flock/`, so `check` needs its `lean-agreement` step. Please record it with the
agreement inputs (`tools/check/check.py --record --on MACHINE`). No pod spend on my side.

**Order with #424 (TM):** put #430 in a train after #424. The Lean auto-merges. The README conflicts in one hunk, since both
edit §1.5 around "Still to prove". To resolve it:
- keep #424's text for the input-copy bullet (`setupH_copySrc_lt` …);
- then keep #430's new "A typed flat class's unit, placed" bullet;
- then keep "Still to prove" with #430's single item (`PastInputs`), since #424 proves the message-bit item.

If you'd rather I resolve it, I'll merge `main` into #430 once TM lands and refile with the new head.
