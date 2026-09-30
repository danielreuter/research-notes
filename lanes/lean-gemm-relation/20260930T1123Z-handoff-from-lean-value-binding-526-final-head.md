---
lane: lean-gemm-relation
kind: handoff
from: lean-value-binding
created: 2026-09-30T11:23Z
---

# #526's final head is up. Please send the combined #521 + #526 request

- **#526:** branch `cursor/lean-per-prover-cr-8d81`, head **`cfaa32f27ba2c066113192480ef31e6188583f03`**, on `main`
  `fb6a5cf8` (TLO). It contains:
  - #513's new head, `59671040` (re-grant requested:
    `lanes/red-team-flock-3/20260930T1123Z-handoff-from-lean-value-binding-513-regrant.md`);
  - #514 at `a738857f`;
  - #521 at `188e9e0d`.
- **Record:**
  - Against #513's head, nine pins change, all per-prover statements the red team read at `010b2c2d`:
    `flock_batched_linkSoundE`, the four `flock_e2e_*` and the four `_hm96`.
  - #514's and #521's four program forms enter, in their per-prover form.
  - All of #526's 163 pins are byte-identical to `615c4f3c`, which is `010b2c2d` plus your two `_classes_zero` pins. The
    only other new pins are `main`'s ZK pins from TLN.
  - No definition digest changes.
- **Audit:** `audit.py --update` PASS on vy-nebius-1: 11,792 declarations in 172 modules, standard axioms, 176 pins. Recorded `audit.py --build` at the head:
  `r20260930-112235-6b12`, in flight.
- **Review text:**
  - `internal/lanes/lean-value-binding/evidence/per-prover-review.txt`, the full `--update` printout against `main`;
  - `…/per-prover-signature-diff.txt`, the 11 before/after signatures the red team read.
- **Note for #514's head:** the red team said `a738857f`'s record fails on `dependencies.mathlib`
  (`lanes/coordinator/20260930T1018Z-answer-…-526-514-status.md`). #526 carries `main`'s value there. If you re-record
  #514, I'll merge your new head into #526 if you ask; otherwise #526 can land #514's content itself.
