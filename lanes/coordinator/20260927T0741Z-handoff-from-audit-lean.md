---
lane: coordinator
kind: handoff
from: audit-lean
created: 2026-09-27T07:41Z
---

# audit-lean -> coordinator: PR #133 (ε_ks at the compiled layer) is ready for the independent Lean build

[PR #133](https://github.com/danielreuter/verity/pull/133), draft; mark it ready when you take it.

- **Branch and tip:** `cursor/audit-compiled-ks-f568` @ `bbeba8a6`. It is stacked on #122
  (`cursor/audit-lean-f568` @ `5f0baa2d`, the PR's base) and has #124 merged in at `e58b957b`, with a conflict
  resolution in the `FlockSoundness.lean` imports and `Check.lean` only.
- **Merge order:** #122 and #124 in either order, then #133. Its diff shows #124's files until #124 merges.
- **The change:**
  - new: `Audit/Extraction.lean` and `Audit/FlockCompiled.lean`;
  - appended: imports, 8 `#print axioms` lines, and `ASSUMPTIONS.md` §9;
  - `test_audit_layer_is_abstract` now also allows `FlockCompiled.lean` to import Flock's theorems;
  - `DESIGN.md` §12 condensed (#122 + #124 + this would otherwise exceed the 48 KB markdown cap). The full rationale
    is now `note:audit-lean/20260927T0736Z-finding-audit-layer-design`.
- **What it proves:**
  - `flock_compiled_knowledgeSound`: the audit's ε_ks holds at the compiled layer, from `table_knowledge_sound_joint`
    used as is, per draw state. It covers one table per session with the leaf layer registered (the demo's
    configuration).
  - `flock_compiled_count`: `δ(K) = miss K + ε_ks(σ) + δ_link(σ)`, where `ε_ks(σ)` is the table theorem's bound
    averaged over the draw.
  - δ_link stays a named hypothesis (it needs Daniel's spec decision), and so does the compiled lowering (level 3).
- **Agreement with flock-soundness:**
  - The ε_ks part uses #124's theorem exactly as their 0650Z handoff specified it.
  - The link hypothesis and the batched-session form are proposed in `lanes/flock-soundness/20260927T0735Z-…` and
    `0738Z-…`. Their reply may change future shapes, but not what this PR proves.
- **Checks:**
  - clean `lake build FlockSoundness` succeeds;
  - `Check.lean` gives 148/148 standard axioms, with no `sorry` or `axiom`;
  - `pytest tests/test_repository.py backends/flock/tests/test_lean_verifier.py`: 11 passed, 2 skipped (`lake` not
    on PATH).
- **Behaviour change:** none (Lean and docs).
- **Please:** run the independent Lean build and axiom audit on `bbeba8a6`, then merge after #122 and #124.
- **Spend:** $0, no pods.
