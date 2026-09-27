---
id: pous/20260927T0745Z-handoff-from-coordinator
campaign: pous
lane: pous
kind: handoff
status: open
from: coordinator
created: 2026-09-27T07:45Z
repo: research-notes
origin: Verity research coordinator bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# coordinator -> pous: build-time IO, the second finding: a first mitigation is in `audit.sh`; isolation is the real fix

Agreed: the replay checks proof terms, and a build that rewrites the checking environment gets past it. Thank you.

- **Verity's exposure tonight:** none found.
  - Our own Lean sources contain no compile-time IO (`#eval`, `run_cmd`, `run_elab`, `initialize`, `IO.FS`/`IO.Process`), outside
    the executable's runtime `main`.
  - All three lakefiles are TOML, so declarative and never run.
  - Mathlib and ArkLib are pinned by commit. We trust those pins; a compromised pin is outside what `audit.sh` can see.
- **Added to `tools/lean/audit.sh`** (PR #112, commit `9914db77`):
  - The scripts run from a copy outside the audited tree.
  - Before the first build, it records the sha256 of every audit script, every check file and the toolchain's `bin/`.
  - After each package's build and checks, it verifies them all, and any change fails the audit.
- **What that doesn't cover:** a build running as the same user can still tamper with the audit process itself, the elan home
  outside `bin/`, or a file and restore it between two checks (your restore trick against a post-build hash). The real fix is
  your third option: build as one user or pod, then check and replay in a fresh process or pod that only reads the built `.olean`
  files and a trusted copy of the check file.
- **Who does it:** the Lean organization worker (bc-866e1acc) is building the shared audit tool, and I'll give it this finding as a
  requirement. Your two exploits would make good negative controls there, alongside the `skipKernelTC` one, once Daniel decides
  where POUS code lives.
