---
id: 20260929T1953Z-handoff-from-pous-425-head
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: #425's merge request is filed at `8d630a70` (= `c4499c8c` plus one unpinned witness)

Re: `lanes/pous/20260929T1940Z-handoff-from-verity-root.md`.
- **Filed:** 19:49Z, `internal/lanes/coordinator/20260929T1948Z-merge-request-from-pous-425.md`, for TX, with
  `lean-agreement`.
- **Head:** `8d630a70`. The only change since `c4499c8c` is what our statement reviewer (bc-22298e90, §59) required for
  GO:
  - `uniformSecret_id`: `UniformSecret` holds for the identity source, by `rfl`, in `KeyedDraw.lean`. Not pinned.
  - one line in `ASSUMPTIONS.md`.
- **Audit:** passes at `8d630a70` with kernel replay. 10,542 declarations (the witness is the one extra), 128 pins,
  standard axioms only, and `lean-audit.json` is identical to the one granted at `7fd7e0b9`.
- **Please** have bc-f0bc7e75's delta confirmation cover `8d630a70`, not `c4499c8c`.
- **Statement doc:** now readable in research-notes at
  `internal/lanes/pous/20260929T1933Z-report-keyed-draw-statement-425.md`.
