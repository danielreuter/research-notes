---
lane: audit-lean
kind: report
created: 2026-09-27T06:10Z
status: open
---

CHECKPOINT d8369a68 (06:29Z) [open] one-stage profile PROVED (d8369a68 on cursor/audit-lean-f568): audit_le/audit_profile/audit_count/audit_drawn with eps_ks + delta_link as named hypotheses (KnowledgeSound, LinkSound; per the flock-soundness KS review), partition instance + audit_cone/audit_cone_count/audit_covered (+ AnchorsSound delta_in), oracle-layer oracle_count/profile/cone from SessionSound; subset_escape/subset_miss exact hypergeometric; axioms propext/choice/Quot.sound only; CPU $0; next: two-stage (a),(b1),(b2), then minimax/tightness/counterexamples
CHECKPOINT ae5db5d3 (06:10Z) [open] Lean audit-level guarantees (one-stage profile, cone corollary, two-stage) per docs/audit-protocols.md §4; branch cursor/audit-lean-f568 from origin/main ae5db5d3; CPU only, $0; agent bc-a0c5a22f; next: install Lean 4.34 + Mathlib cache, write FlockSoundness/Audit/
