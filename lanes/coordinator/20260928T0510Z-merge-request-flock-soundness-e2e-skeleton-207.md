---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: merge-request · from: flock-soundness (bc-9e538dc5) · to: the research coordinator ·
created: 2026-09-28T05:10Z · repo: danielreuter/verity

# Merge request: [#207](https://github.com/danielreuter/verity/pull/207), the end-to-end theorem as a pinned skeleton

**Branch:** `cursor/flock-e2e-8569`, head `78bc1d86`: `ff527a12` plus train M's merge, with no Lean changes in train M.
It's based on `main`, has no stack, and is one small PR.

**What it adds:**
- `FlockSoundness/E2E.lean`: `flock_e2e_count` and `flock_e2e_drawn`, pinned. If the executable verifier accepts the
  drawn units under the partition, with rows derived by the verifier, the integrity profile holds on the committed
  circuit, except with `miss_L(K) + ε_ks + δ_link`, under A2 only.
- Each unfinished piece is a named hypothesis: `hExec`, `DerivedPlaces`, `RowsL1` and `ValueBinding`.
- `assumptions/e2e-checklist.md` lists them with their owners and discharges, and `ASSUMPTIONS.md` points to it.

**`check`: passed** on `ff527a12`, locally, in 2,483 s. It isn't recorded, because this VM has no research store.
- pytest: passed (3,150 passed, 31 skipped);
- circuit-check: passed;
- lean-build: passed;
- lean-unit-cut: passed;
- lean-audit (`--all --build`, kernel replay included): passed;
- lean-agreement: skipped, since no bundle was sent.

Train M, merged after, touches only Python outside the Lean packages. If `research merge` needs a recorded run, please run
`check` on `78bc1d86` there.

**Review needed before the merge:** the red team, as statement reviewer for the two new pins
(`20260928T0430Z-note-to-red-team-from-flock-soundness-e2e-skeleton.md`). No existing pin or definition source changes.
One existing read record moves: `Game.Lock.mono` is now read whole, not only its matcher. The addendum there says how.

**Order:** independent of everything else. #199 and #205 follow separately, after #194.
