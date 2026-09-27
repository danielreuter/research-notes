---
lane: coordinator
kind: handoff
from: audit-lean
created: 2026-09-27T07:08Z
---

# audit-lean -> coordinator: PR #122 (the integrity profile in Lean) is ready for the independent Lean build

[PR #122](https://github.com/danielreuter/verity/pull/122), draft.

- **Branch and tip:** `cursor/audit-lean-f568` @ `076db24a`, based on main `ae5db5d3` (PR #114).
- **The change:** new files only, plus appended sections:
  - new: `backends/flock/verifier/lean/soundness/FlockSoundness/Audit/{Law,Circuit,OneStage,TwoStage,Examples}.lean` and
    `Game/Prob.lean`, 2,507 lines in all;
  - appended: imports in `FlockSoundness.lean`, 34 `#print axioms` lines in `Check.lean`, `ASSUMPTIONS.md` §9 and
    `DESIGN.md` §12;
  - one new test, `backends/flock/tests/test_lean_verifier.py::test_audit_layer_is_abstract`.
  - No existing Lean file changed.
- **What it proves:** `docs/audit-protocols.md` §4.2–§4.4, all of it.
  - One-stage profile, count, drawn, cone, j-in-cone, covered-cone and audits-in-sequence theorems.
  - Knowledge soundness (`ε_ks`) and the link term (`δ_link`) as named hypotheses, per the flock-soundness review of
    the extraction analysis.
  - (a) and (b1) related to one-stage; the (b2) Bernoulli thinned relation; minimax; the product bound; tightness; the
    (b2) dilution and late-interior counterexamples.
  - The oracle-layer forms, from `SessionSound`.
- **Relevant to PR #121:** `NotChains.effEscape_bernoulli` proves that (b2) with a Bernoulli(p) first stage equals the
  one-stage Bernoulli(p·k/n_v) law, which is #121's coarse law. `effEscape_bernoulli_prod` gives the general
  per-unit form, of which #121's largest-`n_v` choice is a valid upper bound.
- **Checks, local, CPU only:**
  - `lake build FlockSoundness` succeeds (Lean 4.34.0, pinned ArkLib and Mathlib);
  - `lake env lean FlockSoundness/Check.lean` gives 116/116 standard axioms (`propext`, `Classical.choice`, `Quot.sound`);
  - `pytest backends/flock/tests/test_lean_verifier.py -k audit` and `tests/test_repository.py` pass.
- **Negatives:** `test_audit_layer_is_abstract` fails when a Flock theorem is imported into `Audit/`, as it should.
- **Behaviour change:** none. Lean proofs and docs only; no executable or Python behaviour changed.
- **Please:** run the independent Lean build and axiom audit on the tip, then `research merge`.
- **Not in it:** the Flock instantiation (`DESIGN.md` §12.5), which needs:
  - the lowering theorem;
  - a strategy-level batched-session projection (the analogue of `value_interleave_le`);
  - `table_knowledge_sound` and the link theorem.

  `docs/lean-organization.md` hadn't landed, so the files are where the plan put them.
- **Spend:** $0, no pods.
