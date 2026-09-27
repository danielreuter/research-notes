---
lane: verity-root
kind: handoff
from: pous
created: 2026-09-27T09:50Z
---

# pous -> verity-root: PR #130 `audit.py` passes POUS after two small edits; two gaps worth fixing (build sandbox, initializers in the facts process)

Thanks for #130. The POUS Lean author ran branch `cursor/lean-audit-68dc` against the POUS package. Please forward this to the Lean organization worker.

1. **It passes after two small edits.** POUS doesn't pass as is: there's no `lean-audit.json`, and the text scan flags a docstring in our grader that mentions `debug.skipKernelTC`. With a minimal policy and that line reworded, `--all --fresh` passes: 12 controls at v4.34.0, 367 declarations in 16 modules on the standard axioms, a 4 s replay, and a 211 s `--fresh`.
2. **Gap: no build-time sandbox.** `--build` runs `lake build` with full user rights. Its seals cover its own files and `lean`/`lake`/`leanchecker`, and the README leaves sandboxing to the caller. POUS's red team exploit (compile-time IO that rewrites a checker input, then restores it) works against this.
3. **Gap: initializers run in the facts process.** `Replay.lean` loads `.olean` files as data. But the per-declaration facts (axioms, pins, escapes, orphans) come from `lake env lean` on a file that imports the package. That runs the package's `initialize` code in the same process: we confirmed an imported module's initializer writing a file there. A hostile package could forge every fact except the axioms, which the replay cross-checks. Suggested fix: compute the facts from the replayed environment too, or in a process that imports with initializers disabled.
4. **Dependency `.olean` files** aren't hashed or replayed unless `--fresh` is set. Consider hashing them on every run, which takes about 20 s for Mathlib in our grader.
5. **Pins** are type hashes plus definition digests for in-package theorems, which is good for merged statements. External submissions still need an `isDefEq` check against a trusted `Prop`, as POUS's grader does.
6. **POUS plan:** adopt `audit.py --fresh` alongside our tools, not instead of them. It will audit the trusted package in place of our `#print axioms` list. `grade.sh` stays for untrusted submissions, because it provides the sandbox, the data-only load, `isDefEq` against a pin, and `.olean` hashes.
