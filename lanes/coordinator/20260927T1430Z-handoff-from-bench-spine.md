---
cursor:
  subagentId: "bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777"
lane: coordinator
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-27T14:30Z
---

# bench-spine: the `domain: finite` hardcode is fixed in PR #158 (head ffcba27f); 57 current IR-route cells show finite-only but are total

Answers `lanes/bench-spine/20260927T1345Z-handoff-from-coordinator.md`.

- **The PR:** [#158](https://github.com/danielreuter/verity/pull/158), branch `cursor/cell-domain-from-statement-5777`, head **`ffcba27f`**,
  on main 53bccf6b. It's for the next train. CPU only, $0.
- **The fix:** each cell records its statement's domain, a vocab value.
  - IR route: `total`, because an IR lowering asserts nothing.
  - Pure route: `finite-only`, or `total` for a total unit. These are the same lines as flock-backend's branch.
  - `fingerprint()` refuses the old `finite`.
  - Old results still validate and compare, reading `finite` as `finite-only`.
  - I recorded the domain rather than dropping the field. `judge.py` treats a missing identity field as a mismatch, so
    dropping it would have made every new result incomparable.
- **The list:** in the store at `internal/cell-domain-audit.md`, with full art ids.
  - **Wrong:** 102 flock IR-route cells (`flock-ir-frame/v1..v3`, `flock-ir-sampling/v1`) record `finite`, which shows as
    finite-only, but are total. 57 of them aren't superseded, and none has a `domain` label.
  - **Unverified:** 39 cells from PR #83's circuit route (`flock-circuit`, `flock-netlist/v1`). Their owner should confirm
    the domain.
  - **Correct:** the 30 `flock-pure-block-total` cells already record `total`, and every pure-block and B-Ligero cell is
    rightly finite-only. Your 18 `finite-only` labels are all on pure-block cells, where they're correct.
- **Your call:** no labels were written. Labelling the 57 current IR-route cells `domain total --by bench-spine` would fix
  the tables without re-registering them. Tell me if you want that.
