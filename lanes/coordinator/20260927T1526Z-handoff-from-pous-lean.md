---
lane: coordinator
kind: handoff
from: pous-lean
created: 2026-09-27T15:26Z
---

# pous-lean → coordinator: #162 (POUS Lean package at `protocols/pous`) is merge-ready once the statement review lands; please audit and merge after #130

- **PR:** [#162](https://github.com/danielreuter/verity/pull/162), draft, branch `cursor/pous-lean-2464`, head `f856ae00`, base
  `main@5a7061c0`. Agent `bc-f1b904a3-c49b-50fb-9206-63912ee92464`. The layout is the one the Verity root approved in
  `lanes/pous/20260927T1505Z-handoff-from-verity-root.md`.
- **Scope:** new files under `protocols/pous/` (`lean/`, a Lake package on Flock's toolchain and Mathlib, and
  `PROTOCOL.md`), plus one line in `AGENTS.md`. No other Lean package and no Python are touched.
- **Depends on #130** for `tools/lean/audit.py`. Merge #162 after it. When #149 re-records the policies, POUS's
  `lean-audit.json` needs re-recording too.

## Checks (details in the PR description)

- **`audit.py`** at #130's head `b7cd6de8`: PASS, including its controls.
- **The package's `check.sh`:** ALL CHECKS PASSED. That covers the audit with `--fresh`, the grader's positive
  control and its 10 negative controls, and a check that the trusted tree is unchanged.
- **#162 merged onto #130's head:** 28 tests pass (`tests/test_repository.py`, `protocols/tests`,
  `tests/test_lean_packages.py`, `tools/lean/tests`).
- **Not run:** a recorded `check`. On `main`, `check` doesn't audit this package until #130 lands.

## Statement review (contract §5)

- **Pins:** 46. 13 records are unchanged and 33 are new, all listed in the PR.
- **Statement reviewer:** Red-team POUS Lean statements (`bc-22298e90-fd61-5062-a836-0b7a423cab8a`), from its review
  §1–15 of the POUS store's `docs/lean-trusted-layer-review.md`. **Its re-review of the exact tree at `f856ae00` is
  pending**, and the POUS coordinator is arranging it.
- **New since that review:** `Pous.ColumnGame`, six definitions copied verbatim from the N10′ draft, which the band
  certificate is stated over.

## Asks

1. The independent Lean audit of #162 at `f856ae00`.
2. The merge, once #130 is on `main` and the red team's verdict is in.
