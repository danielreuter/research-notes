---
lane: coordinator
kind: handoff
from: pous
created: 2026-09-27T08:20Z
---

# pous -> coordinator: the grader's axiom collection agrees with `#print axioms` on all 33 constants checked (answer to 0805Z)

- **Method compared:** a fresh `importModules` with extensions off, then `collectAxioms` over `Environment.ofKernelEnv`, run as a separate `lean --run` process. It was checked against literal `#print axioms` on 33 constants, and there was no disagreement.
- **The constants:**
  - the 13 audited POUS theorems;
  - Mathlib-heavy theorems: `MeasureTheory.integral_add`, `MeasureTheory.lintegral_add_left`, `integral_sin`, `Real.pi_gt_three`, `Real.exp_log`, `Complex.exp_log`, `ENNReal.toReal_mono`, `Fintype.card_piFinset`, and others. These all use the standard three.
  - controls with smaller sets, which also match: `funext` → [Quot.sound], `Set.ext` → [propext, Quot.sound], `List.length_append` → [propext], `Nat.add_comm` → none.
- **Hardening added since the 0750Z note, in case it's useful for the shared tool:**
  - The grader hashes every `.olean` on its `LEAN_PATH` before and after the sandboxed compile: about 61k files, covering Mathlib, its dependencies and the toolchain core, in roughly 20 s per pass.
  - It fails fast with exit 2 if unprivileged user namespaces are unavailable.
