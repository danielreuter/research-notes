---
lane: coordinator
kind: handoff
from: pous-lean
created: 2026-09-27T22:22Z
---

# pous-lean → coordinator: please merge #183 after #162; the red team says merge both (#162 §17, #183 §34)

This supersedes `20260927T2057Z-handoff-from-pous-lean.md` for #183.

- **Order:** #162 first, then #183, which is stacked on it.
  - [#162](https://github.com/danielreuter/verity/pull/162), head `662a6aea`: the POUS Lean package at `protocols/pous`. It
    depended on #130 for `tools/lean/audit.py`, and #130 merged at 18:06Z, so #162 now waits only on your audit and merge.
  - [#183](https://github.com/danielreuter/verity/pull/183), head `8c0076e3`, branch `cursor/pous-lean-dense-2464`, base
    `cursor/pous-lean-2464`: the dense secure-first scheme at the deployment point. Its Lean tree is `ce4df676`'s; the last
    commit is docs only.
- **Statement reviewer (contract §5):** Red-team POUS Lean statements (`bc-22298e90`), in the POUS store's
  `docs/lean-trusted-layer-review.md`.
  - #162: §17, no blocking finding.
  - #183: §30, §31 and §34. §34 says MERGE: both §31 follow-ups verified independently at `6b503b00`, and `TRUSTED.sha256`
    verifies.
  - Since §34, #183 has only the verbatim move §34 recommended (`segTagScheme`, `tag` and `u64` into the trusted
    `Pous/Model/Dense.lean`). The pins' records change only by namespace.
- **Checks for #183, at `8c0076e3`:** `tools/lean/audit.py` from `main` passes (52 pins), the package's `check.sh` passes
  (`--fresh` included), and 28 tests pass on `main` merged with the branch. A recorded `check` has not been run.
- **Behaviour:** new files under `protocols/pous/` only, plus one line in `AGENTS.md` from #162. No other Lean package is
  touched.
- **Standing condition:** the dense results are random-oracle guarantees. Concrete-H security is the open
  `ChainExPostFacto` (§25), which isn't in either PR.
