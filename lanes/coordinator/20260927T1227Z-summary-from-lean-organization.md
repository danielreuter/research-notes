---
cursor:
  subagentId: "bc-866e1acc-6010-57e8-b0f8-ec01aced68dc"
---

lane: coordinator · kind: summary · from: lean-organization · created: 2026-09-27T12:27Z

**#130 (the Lean audit in `check`) is at `b7cd6de8` on train F (`5a7061c0`, with #146), as of 15:35Z.** The pins are re-recorded on #146's final Merkle definitions, adding `collision_hash`, `all_sized` and the three explicit `*_inputs` reductions. `check` passed (`r20260927-145832-f566`) and the merge gate accepts it. It waits for red-team-flock-3's statement verdict, with flock-verifier confirming intent. The commit taking the executable's `lean-audit.json` out of #134's agreement cache key waits for #134's rebase. **#149, POUS's follow-up on #130, is at `6741026f`.** The audit now reads facts with initializers off, builds in a sandbox, and refuses compile-time code. It checks the dependencies' `.olean` digests, gives a template for a missing policy, and has `--all --build` install the toolchain before the controls. All 16 controls pass, from an empty home directory too.
**Waiting on Daniel** (`docs/lean-organization.md` §7): moving statement-defining definitions out of the soundness proof files, with `layers` rules; retiring the old `CheckAxioms`/`Check.lean` lists, which is possible now that #113, #118 and #122 have landed; where POUS's code lives; a nightly `--fresh` run, about 30 minutes on a CPU pod with at least 16 GB; and build caching for `check`'s audit.
