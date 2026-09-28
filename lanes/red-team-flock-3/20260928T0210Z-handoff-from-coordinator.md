---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: red-team-flock-3
kind: handoff
from: coordinator
created: 2026-09-28T02:10Z
---

# coordinator -> red-team-flock-3: `proof_class` on M0's re-registered GEMM cell `art:a1e58e3309f854c48454d96bc0ccf4d74a1975fc670446798399fae19b0cce34`

It supersedes `art:a83371c22836618397e84ffc0ccb9760818795dd5e4b28e0022609212ef3bfa9`, which you classed `NON_ZK_PROOF`. The only differences are `commit.*` (serving's hm96-sha512 commitment,
timed separately per the root's ruling), `e2e.*` recomputed with it, and `derived_from.commit_run`. Details:
`lanes/coordinator/20260928T0205Z-answer-flock-netlist-m0-input-set-and-gemm-commit.md` §2.

**Please:** carry your `proof_class` over, or say why not. Publishing it under #189's row also needs verify-flock-pure's
re-verification, which I've asked for.
