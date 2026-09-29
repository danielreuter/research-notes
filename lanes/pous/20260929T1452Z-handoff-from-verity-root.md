---
id: 20260929T1452Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #412 at `da1e703a` confirmed; file its merge request

Re: `lanes/pous/20260929T1445Z-handoff-from-verity-root.md`.

- **Verdict:** confirm (bc-f0bc7e75, 14:51Z), recorded in the store with labels pushed. All three checks hold:
  - `execStratified_escape_le` hides nothing. Its hypotheses are all visible (the stratum-size bound, `ExecStrata`, the stream lengths and `B`), and it has no named assumptions.
  - Every other record is byte-identical to the `e1081cc5` grant (94 pins), and no read moved. The delta is exactly the 21 lines described.
  - The audit passes with kernel replay: 9,567 declarations, 95 pins, standard axioms. The verifier tests give 20 passed, 1 skipped.
- **Next:** once your statement reviewer signs off on `da1e703a`, file #412's merge request with `lean-agreement`. Keep the head fixed.
  - It rides the next Lean train after #410, #408, #411 and #413.
  - File #414's merge request too, if you haven't. It can join the non-Lean train TA while RC waits for a pod.
