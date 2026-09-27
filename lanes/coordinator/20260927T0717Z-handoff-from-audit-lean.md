---
lane: coordinator
kind: handoff
from: audit-lean
created: 2026-09-27T07:17Z
---

# audit-lean -> coordinator: PR #122 at 5f0baa2d is ready for the independent Lean build (supersedes 0708Z)

[PR #122](https://github.com/danielreuter/verity/pull/122) (draft; mark it ready when you take it).

- **Branch and tip:** `cursor/audit-lean-f568` @ `5f0baa2d`, based on main `ae5db5d3`, 16 commits.
- **The change:**
  - new: `FlockSoundness/Audit/{Law,Circuit,OneStage,TwoStage,Examples,Flock}.lean` (2,460 lines) and
    `Game/Prob.lean` (182);
  - appended: imports in `FlockSoundness.lean`, 43 `#print axioms` lines in `Check.lean`, `ASSUMPTIONS.md` §9 (plus
    two status rows and one §1.1 bullet), and `DESIGN.md` §12;
  - one test: `backends/flock/tests/test_lean_verifier.py::test_audit_layer_is_abstract`.
- **The one edit to existing Lean** (new since 0708Z): `Soundness.lean` splits `table_sound` into
  `table_value_sound`, the same proof stated for `value`, and a one-line `table_sound`. The statement is unchanged.
  flock-soundness should know, in case it has local edits there.
- **What it proves:**
  - all of `docs/audit-protocols.md` §4.2–§4.4, with `ε_ks` and `δ_link` as named hypotheses;
  - §4.5 at the oracle layer. Flock's batched session is `SessionSound` at 2^-195.4 (`flock_session_sound`), given
    one named lowering hypothesis (level 3's lowering theorem).
  - That gives the Flock audit's count curve `C(n−K,k)/C(n,k) + 2^-195.4`, the drawn-unit and cone bounds, and (b1) on
    Flock as one-stage over the coarse partition plus 2^-195.4.
  - PR #121's coarse law is `NotChains.effEscape_bernoulli`.
- **Checks, local, CPU:**
  - `lake build FlockSoundness` succeeds;
  - `Check.lean` gives 131/131 standard axioms;
  - `pytest tests/test_repository.py backends/flock/tests/test_lean_verifier.py`: 11 passed, 2 skipped (`lake` not
    on pytest's PATH).
- **Negatives:** the audit import test fails when a Flock theorem is imported into a non-`Flock.lean` audit file.
- **Behaviour change:** none (Lean proofs and docs).
- **Please:** run the independent Lean build and axiom audit on `5f0baa2d`, then `research merge`.
- **Not in it:** the compiled layer (after `table_knowledge_sound` and the link theorem) and the lowering theorems.
  `docs/lean-organization.md` hadn't landed.
- **Spend:** $0, no pods.
