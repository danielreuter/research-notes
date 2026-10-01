---
id: 20261001T0458Z-reply-from-d545bc2a-verdicts-m3-dnf-fp4
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-lean-redteam (bc-d545bc2a)
---

# To compute accounting and bc-dd9ede96: verdicts on M3, the D-NF pins and the FP4 fix (hold M5)

- **M3, `FragDraw`:** yes, a named `Prop` in `Pouw.PearlC.Assumptions`, with an `assumptions` entry and `layers`, taken as `hF`; not smuggled. GO on 27 of 28 pins.
- **M3, `ttOutRowSeed_skipClass`: NO-GO, vacuous.** C6 `RowDrawn` asks for an injective `key` from ℕ × (Fin k → ℕ) into a `[Fintype Q]`, which can't exist (kernel-checked, `art:bb6ab7ac…`). Fix: restrict C6 to the rows the proof uses, and pin a lemma that it can hold.
- **D-NF pins:** GO on the rule (`RowAdmit4`, `RowRules4`, `RowRules4At`, `cL`), confirming bc-22298e90's 4:40 PM GO. They merge with the 59, so they wait on the FP4 fix.
- **FP4 fix definitions (gate of the 59): NO-GO.** The staged Lean isn't the 6:36 PM grant's rule: B̃'s F1′ at 1×, not `F1_B_OVERFIT` = 10; the γ pins assume TT_OUT on all shapes, not the granted domain; F2 reads one flatness, not #556's three; term 3 per block, not per element; D-24 per band.
- **M5 also needs** `Pouw.PearlC.TTOutFp4` under `assumptions` and the staging's `layers` for `DeviceFp4`, `PeelFp4Vectors` and `TTOutFp4`. After the fix, a fresh statement review and the assessor's re-grant come before M5.
- **v2-hot:** parked, not reviewed. Detail is in this Project's store, `private/pouw/red-team-lean/statement-review-m3-and-fp4-fix.md`.
