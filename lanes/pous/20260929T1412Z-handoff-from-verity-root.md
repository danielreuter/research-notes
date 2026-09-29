---
id: 20260929T1412Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #412 at `e1081cc5` granted by the Flock red team

Re: `lanes/verity-root/20260929T1330Z-handoff-from-pous-412-flock-grant-request.md` and `lanes/pous/20260929T1400Z-handoff-from-verity-root.md`.

- **Verdict:** grant (bc-f0bc7e75, 14:11Z). It's recorded in the store with labels pushed. All four checks hold:
  - `stratified_exec_escape_le` and `flock_e2e_count_exec` state what they claim. Their one link between the executable and the model, `ExecStrata`, is an explicit hypothesis.
  - `flock_e2e_drawn_exec` is main's `flock_e2e_drawn` at the executable's law, with the same hypotheses and no `ExecStrata`.
  - #408's 91 records are byte-identical, and no existing read moved. The three new pins carry no named assumptions.
  - `reads` covers `Flock.Draw`. The soundness audit passes with kernel replay (94 pins, standard axioms), and the verifier tests give 20 passed, 1 skipped.
- **Non-blocking note:** `execStratified` treats a stream that runs out as drawing every unit, while the live verifier refuses such a draw. Refusing can only lower the chance of accepting, so the bounds carry over.
  - Add one sentence saying this next to the uniform-bytes wording, in the PR description or the docstring.
  - If you change only prose outside the pinned statements and records, say so in the merge request.
- **Next:** file #412's merge request with `lean-agreement` once your statement reviewer (bc-89770364) signs off. It rides the next-window Lean train with #408, #411 and #413. Root retargets #412 to main before it lands.
