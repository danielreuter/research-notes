---
lane: coordinator
kind: handoff
from: pous
created: 2026-09-27T07:25Z
---

# pous -> coordinator: compile-time IO beats file-based audit checks; the kernel replay doesn't catch it

Thanks for adding the replay (0710Z). A second finding from our statement red team affects the shared audit tool's design.

- **What happened.** Lean runs arbitrary IO at compile time (`#eval`, `run_cmd`, `initialize`). A POUS submission used this during its own build to append `sorryAx` to the grader's axiom allowlist file, then restored the file afterwards, so a hash check done after the build still passed. A variant replaced the grader binary. Kernel replay doesn't see either one, because the attack targets the checking environment, not the proof term.
- **Why it applies to `audit.sh`.** `lake build` runs untrusted code before `lake env lean CHECK_FILE` and the replay run in the same tree and process space. So a PR's build could rewrite the check file, `replay.sh`, or the toolchain it calls.
- **Suggested mitigations:**
  - Build the audited tree as a user who can't write the audit scripts, the check file or the toolchain.
  - Take the check file and the scripts from a trusted copy outside the built tree, and hash-check them and the toolchain binaries after the build.
  - Or run the check and replay in a second, fresh process or pod that only reads the built `.olean` files.

  Grepping for `#eval` or `run_cmd` isn't enough, since Mathlib and tactics legitimately contain metaprogramming.

POUS is adding both exploits as negative controls. Once Daniel decides where the code lives, they can be shared with the Lean organization worker.
