---
lane: red-team-flock-3
kind: handoff
from: lean-value-binding
created: 2026-09-30T11:45Z
---

# Combined grant request: #514 `f3a60a36`, #521 `4e4ee3e4` and #526 `04b94af7`, all on `main` `fb6a5cf8`

lane: red-team-flock-3 · from: lean-value-binding (bc-a84aadb3), for lean-gemm-relation (bc-590cc416) too, at root's
request · to: red team (bc-f0bc7e75); cc research coordinator, verity-root · repo: danielreuter/verity

This is the one combined request (lean-gemm-relation's 11:27Z handoff made me the sender). It replaces my 09:52Z #526
request and lean-gemm-relation's 08:53Z #514 request. #513's re-grant (`59671040`, 11:23Z) is separate and still open.

**The request:** `grant statement-reviewer` and `grant red-team` on each of:
- `pr:514@f3a60a3641afaa92cacfcd62368bfba9beb4bbf7`
- `pr:521@4e4ee3e4448357b57a4499bd1886409a204eb360`
- `pr:526@04b94af77dea7ccdd7aca274c39fc0eb0fb05510`

**Merge order for RC:** #513, #514, #521, #526. Superseded heads that must not go into a train: `a738857f`, `a19d2871`,
`188e9e0d`, `aa43e99b` and `cfaa32f2`.

## #514 at `f3a60a36` (lean-gemm-relation's; you approved the statements at `a738857f`, 10:16Z)

- It merges `main` `fb6a5cf8` into `a19d2871` and re-records.
- The delta from what you approved is the `dependencies.mathlib` line, now `main`'s `565ec6d0…`, plus the merge of `main`.
- #514's six pin records are byte-identical to `a19d2871`'s. The other 157 pins and every other field equal `main`'s.
- `audit.py --update` PASS: 11,631 declarations in 166 modules, 163 pins.
- Source: `lanes/lean-value-binding/20260930T1127Z-handoff-from-lean-gemm-relation-514-521-on-main.md`.

## #521 at `4e4ee3e4` (lean-gemm-relation's; contains #514 `f3a60a36`)

- It adds `UProg.zeroCols_of_classes` and the two forms `UProg.flock_e2e_{count,drawn}_classes_zero`.
- Their records are identical to `aa43e99b`'s, and to `188e9e0d`'s apart from the Mathlib line. Everything else equals
  #514's new record.
- As #521 has it, their `hCR` is #514's every-prover shape. #526 restates them per prover.
- `audit.py --update` PASS: 11,640 declarations, 165 pins.

## #526 at `04b94af7` (mine; you read its statements at `010b2c2d`, 10:06Z: right, C1–C3 met)

- **What it is:** A2 asked of the prover bounded.
  - `LinkCR` and `linkBoundCR`.
  - `flock_batched_linkSoundE` is `LinkSound linkBoundCR`, with no A2 hypothesis.
  - Every `flock_e2e_*`, `_exec`, `UProg.*` (with `_classes` and `_classes_zero`) and `_hm96` takes
    `hCR : LinkCR … (reg σ) (cont σ) …`.
  - Also your C2 and C3 on #513, as in #513's `eee9c27d`.
- **Since `010b2c2d`**, the delta your 10:06Z note asked about:
  - #521 merged in, with its two `_classes_zero` forms restated per prover, as `_classes` is (`12548d63`);
  - `main` `fb6a5cf8` and #513's new head `59671040` merged in;
  - #514 `f3a60a36` and #521 `4e4ee3e4` merged in (`04b94af7`). The tree is byte-identical to `cfaa32f2`'s, because those
    heads only re-record on the same `main`.
- **Record against `main`**, checked by script:
  - The 163 pins you read at `010b2c2d`, plus #521's two in their per-prover form, are byte-identical to `615c4f3c`.
  - The rest are `main`'s: TLN's 13 ZK pins, and TLO's `Flock.Draw` group, which gains the `_exec_hm96` readers.
  - Against #513's head: nine per-prover pins change (`flock_batched_linkSoundE`, the four `flock_e2e_*`, the four
    `_hm96`), and #514's and #521's four program forms enter.
  - No definition digest changes.
- **Audit:** `audit.py --update` PASS at this tree: 11,792 declarations in 172 modules, standard axioms, 176 pins. The
  recorded `audit.py --build` at `04b94af7` is `r20260930-114448-9445`, in flight.
- **Printouts** (Project store):
  - `internal/lanes/lean-value-binding/evidence/per-prover-signature-diff.txt`: the 11 before/after signatures you read;
  - `…/per-prover-review.txt`: the full `--update` printout against `main`.
- **Push:** my GitHub token is dead, so `04b94af7` is in `artifacts/cursor-lean-per-prover-cr-8d81-04b94af7.bundle`
  (sha256 `59436f70…`, needs `main` `fb6a5cf8`) for root to push. Until then, GitHub's #526 still shows `cfaa32f2`.

Please answer in `lanes/lean-value-binding/`, cc `lanes/lean-gemm-relation/`.
