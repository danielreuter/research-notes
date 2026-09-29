---
id: 20260929T0222Z-handoff-from-pouw-mvp-flock-suite-inputs
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-mvp
---

# `check` fails `verity-flock` once the Lean verifier is built: its suite doesn't declare `protocols/one_stage` (one-line fix)

From the PoUW MVP owner (bc-dd22acf8), for `main`'s owner.

- **Failure:** recorded `check` `r20260929-015410-5a20`, on #315's `d5c175ca`.
  - Its pytest step failed on `verity-flock` alone. All 343 tests passed, with 6 skipped. The suite guard failed it
    for reading 4 files outside its inputs, all under `protocols/one_stage/verity_one_stage/`.
  - Every other step passed: `circuit-check`, `lean-build`, `lean-unit-cut` and `lean-audit`. The Lean agreement step was
    skipped, as usual without its bundle.
- **Cause:** `backends/flock/tests/test_lean_verifier.py:297` (`_one_stage_draw`, from `main`'s `ebc94ac5`) imports
  `verity_one_stage`.
  - It does so only when the Lean verifier binary (`backends/flock/verifier/lean/.lake/build/bin/flock-verify`) is already
    built. In a cold checkout, `check` builds it in the concurrent Lean group, so the tests skip and the suite passes.
  - `backends/flock/pyproject.toml` declares neither `verity-one-stage` as a dependency nor `protocols/one_stage` as a
    test input. So in a warm tree, where the binary is built, the guard flags the import, whether it reads the `.py` or
    its bytecode.
  - A cached cold pass hides it, because the suite cache's key doesn't include the binary.
- **The one-line fix:** in `backends/flock/pyproject.toml` `[tool.verity.tests]`, change
  `inputs = ["backends/direct", "census", "tools/circuit_check"]` to
  `inputs = ["backends/direct", "census", "protocols/one_stage", "tools/circuit_check"]`.
- **Status:** I committed it on #315's branch as `4073474c`, its own commit, but can't push it yet: this VM's GitHub
  token is invalid. Land it on `main` directly if you prefer, and #315 will take it from `main`.
