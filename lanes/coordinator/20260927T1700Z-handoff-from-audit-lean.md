---
lane: coordinator
kind: handoff
from: audit-lean
created: 2026-09-27T17:00Z
---

# audit-lean -> coordinator: PR #171, the compiled-layer audit with δ_link discharged, ready for the independent Lean audit

- **[PR #171](https://github.com/danielreuter/verity/pull/171)** is at `c4d4d469` (branch `cursor/audit-link-composed-f568`).
  Its base is flock-soundness's [#163](https://github.com/danielreuter/verity/pull/163) at `7516258b`, the link theorem,
  which is on #127. The delta is one new file, `Audit/FlockLinked.lean`, plus a few lines in `Check.lean`, the test and the
  docs.
- **What it proves.** `flock_batched_count_linked` and `flock_batched_drawn_linked` compose `flock_batched_linkSoundE`
  into the expected-time batched audit (`flock_batched_countE`/`drawnE`) at the plurality value layer. So the
  compiled-layer bound carries **no `δ_link` hypothesis**: `δ(K) = miss_L(K) + ε_ks(σ) + linkBoundE`, with
  `linkBoundE = Q_s/(1−ρ)·(2t'(1+k)/2^256.5 + 1/(eM) + k/(eR_w))`.
- **What it rests on, all named:**
  - A2 for the link theorem's finders;
  - `ValueBinding` (the `hm96-sha512` leaf layout discharges it);
  - BCHKS25 Theorem 4.6;
  - the lowering. In the `_placed` forms that is each drawn unit's `UnitPlace`: the row placement of #154's
    `placement_stack`, plus L1 through the audit circuit's rows.
- **Checks:**
  - `lake build FlockSoundness` succeeds;
  - `Check.lean` gives 229 of 229 standard axioms, with no `sorry` or `axiom`;
  - the repository and Lean-verifier tests give 17 passed, 1 skipped;
  - CPU only, $0.
- **Merge order:** after #127 and #163. The `_placed` forms meet #154's `placement_stack` once #154 and #171 are both in.
  That wiring is a short follow-up, and nothing else changes.
