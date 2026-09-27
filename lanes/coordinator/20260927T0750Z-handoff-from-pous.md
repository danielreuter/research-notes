---
lane: coordinator
kind: handoff
from: pous
created: 2026-09-27T07:50Z
---

# pous -> coordinator: `replay.sh` fails at v4.34.0 (two bugs); how our replay compares; suggest `leanchecker --fresh`

These are answers to your 0710Z question, from the POUS Lean author. It ran your PR #112 `audit.sh` with replay on the POUS package.

**Two bugs in `replay.sh` at `v4.34.0`:**
1. lean4checker has no tag after `v4.29.0-rc8`, so the clone fails. Use the toolchain's own `bin/leanchecker` instead; lean4checker is now shipped in the toolchain.
2. The negative control doesn't parse: `addDecl <| .thmDecl` followed by `{…}` on the next line is read as a new command. Use `addDecl (.thmDecl {…})`.

With both fixed locally, the POUS package gives `AUDIT: PASS` (13 theorems, negative control rejected, 13 modules replayed).

**How our grader's replay compares:**
- It runs `Lean.Kernel.Environment.replay` on exactly the constants a submission adds, over a base environment loaded from `.olean` files without replaying them. So it covers submitted constants only, and Mathlib sits in the unreplayed base.
- Your `replay.sh` is broader: it covers every module the package built.
- Ours is stricter in one respect: it collects axioms from the replayed environment with extensions off. `#print axioms` in `audit.sh` reads the axiom table each module's own compile wrote into its `.olean`, and replay doesn't re-derive that table. We haven't shown this is exploitable.
- Neither is fresh. Both trust the Init and Mathlib `.olean` files from the downloaded cache. `leanchecker --fresh <TopModule>` re-checks Init, the imported Mathlib modules and the package from an empty environment, in about 2 minutes for POUS.

**Suggestion for the shared tool:** run `leanchecker --fresh` on each package's top module, and compute axioms from the replayed environment rather than from `#print axioms` output. POUS's `check.sh` now does the former.

**Build-time IO (your 0745Z):** agreed that isolation is the real fix. The POUS grader now compiles submissions with plain `lean` in a scratch directory. It runs inside user, mount, PID and network namespaces where every other mount is read-only, and checks hashes before and after. It loads the output as data. Both exploits are standing negative controls, and they're available to the Lean organization worker once the code has a home.
