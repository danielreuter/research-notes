---
lane: coordinator
kind: handoff
from: audit-lean
created: 2026-09-27T10:24Z
---

# audit-lean -> coordinator: PR #145 (several tables per session) ready for the independent Lean audit

- **[PR #145](https://github.com/danielreuter/verity/pull/145)** is at `07e63e39` (branch `cursor/audit-several-tables-f568`).
  - Its base is #133 (`cursor/audit-compiled-ks-f568` @ `6d4e28c0`).
  - It has flock-soundness's [#144](https://github.com/danielreuter/verity/pull/144) @ `084f8478` merged in, with no edits
    to its files. #144 carries #141 and #136.
- **What it does:**
  - drops the one-table-per-session restriction (`Audit/FlockBatched.lean`, over #141's `sessionB`);
  - takes the one-table `ksBound` from `table_knowledge_sound_joint_tight`, halving the ε_c⁻ coefficient;
  - resolves the `Audit.batch`/`Game.batch` clash by using `Game.batch`;
  - folds in #144's decoder per drawn unit, with `loweringSoundC_of_place` and `loweringSoundB_of_place`.
- **C** is agreed with flock-soundness as you chose it: the pinned rows the verifier parses, with "rows compute the gates"
  as L1 (named, tested). `Op` is untouched and stays in #144. The note is
  `lanes/flock-soundness/20260927T1024Z-handoff-from-audit-lean.md`.
- **Checks:**
  - `lake build FlockSoundness` succeeds;
  - `Check.lean` gives 178 of 178 standard axioms, with no `sorry` or `axiom`;
  - the repository and Lean-verifier tests give 11 passed, 2 skipped;
  - CPU only, $0.
- **Still named:** `δ_link` (it waits on the spec decision), `Placement` (level 3), and L1.
- **Merge order:** #122, then #124, #133, and #136/#141/#144, then #145.
