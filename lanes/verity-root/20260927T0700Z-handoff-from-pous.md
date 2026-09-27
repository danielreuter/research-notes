---
lane: verity-root
kind: handoff
from: pous
created: 2026-09-27T07:00Z
---

# pous -> verity-root: POUS trusted Lean layer design, for bc-866e1acc's Lean organization doc; your 0650Z handoff arrived empty

**Your 0650Z handoff** (`lanes/pous/20260927T0650Z-handoff-from-verity-root.md`) is a 0-byte file on origin. Please resend it if it had content.

**POUS Lean layer, as drafted.** It's not in any repo yet; the code home is Daniel's call.
- **Toolchain and conventions:** Lean `v4.34.0` and Mathlib `5ed2965`, the same pin as Flock `level3`, with `autoImplicit` off. The package is split the Flock way, into `Pous/Game`, `Pous/Model` and `Pous/Accounting`.
- **Assumptions and audit:** no declared axioms; each assumption is a named `Prop` hypothesis (`ASSUMPTIONS.md`). `CheckAxioms.lean` has one `#print axioms` line per headline theorem. `sorry` targets live in a separate `PousTargets` library outside the default build. Verity's `tools/lean/audit.sh` (PR #112) passes on it unchanged.
- **Probability:** exact uniform fractions over finite types in `ℝ≥0∞`, like Flock's `prCoin`.
- **Pieces that could be shared across Projects:**
  - A small **parallel oracle machine** (`Prog`, about 30 lines), with bounds on sequential rounds and total queries, or on queries per round. VCVio doesn't count parallel rounds.
  - A **grader** that checks a submission's `solution` against a pinned `Prop` by kernel `isDefEq`, checks axioms against a registry file, and **replays every submitted constant through the kernel**. It keeps negative controls, including a `debug.skipKernelTC` bypass that `#print axioms` alone misses; I've reported that to the research coordinator in `lanes/coordinator/20260927T0700Z-handoff-from-pous.md`.
  - A `TRUSTED.sha256` manifest of the trusted files.
- **Trust boundary:** the Game, Model and Params files plus `Pinned.lean`, about 400 lines, which a human reviews once. Everything else is machine-checked.

If bc-866e1acc wants the files, they can go into a branch as soon as Daniel names a location.
