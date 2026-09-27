---
lane: audit-lean
kind: report
created: 2026-09-27T06:10Z
status: open
---

CHECKPOINT d48dfb61 (06:37Z) [open] two-stage PROVED (d48dfb61, PR #122): twoStage_profile (b) over coarse partition with effEscape, eps_ks/delta_link at fine level; effEscape_full ((b1) = one-stage over coarse); two_stage_a_coarse; full lake build FlockSoundness OK, Check.lean 100/100 standard axioms; next: minimax (uniform optimal), (b2) Bernoulli/thinned formula, tightness + two counterexamples, then DESIGN/ASSUMPTIONS docs
CHECKPOINT d8369a68 (06:29Z) [open] one-stage profile PROVED (d8369a68 on cursor/audit-lean-f568): audit_le/audit_profile/audit_count/audit_drawn with eps_ks + delta_link as named hypotheses (KnowledgeSound, LinkSound; per the flock-soundness KS review), partition instance + audit_cone/audit_cone_count/audit_covered (+ AnchorsSound delta_in), oracle-layer oracle_count/profile/cone from SessionSound; subset_escape/subset_miss exact hypergeometric; axioms propext/choice/Quot.sound only; CPU $0; next: two-stage (a),(b1),(b2), then minimax/tightness/counterexamples
CHECKPOINT ae5db5d3 (06:10Z) [open] Lean audit-level guarantees (one-stage profile, cone corollary, two-stage) per docs/audit-protocols.md §4; branch cursor/audit-lean-f568 from origin/main ae5db5d3; CPU only, $0; agent bc-a0c5a22f; next: install Lean 4.34 + Mathlib cache, write FlockSoundness/Audit/
