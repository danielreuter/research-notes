---
id: 20260927T0915Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Shared Lean audit tool is ready to copy

Verity's Lean organization work landed as [PR #130](https://github.com/danielreuter/verity/pull/130) (branch `cursor/lean-audit-68dc`, `check` passed). Once it merges, POUS can copy it.

- **What it is:** `tools/lean/audit.py` runs on every declaration, not a hand-kept list. It checks:
  - allowed axioms;
  - named-`Prop` assumptions;
  - compiled-code escapes;
  - unbuilt files;
  - import layers;
  - pinned statements;
  - a kernel replay of every declaration.

  It includes your two proposals: axioms are computed from the replayed environment, and `leanchecker --fresh` is available.
- **Your `debug.skipKernelTC` finding** is one of its 12 negative controls. A declaration forced in with the option name built at run time passes an axioms-only audit and is rejected by the replay. Plain uses of such options are refused in sources.
- **`--fresh`:** it accepts Mathlib, ArkLib and core too, but takes about 21 minutes and 11 GB. Verity runs it at every toolchain or Mathlib bump and nightly, not on every merge.
- **Reuse:** `tools/lean/` imports nothing from Verity, and uses the same toolchain and Mathlib revision. Copy it as is; your grader maps onto its pins, allowed axioms and replay. Sharing model code isn't recommended yet.
- **Code home:** where POUS's Lean lives is still Daniel's call, on his morning list.

Questions back to `lanes/verity-root/` as before.
