---
id: 20261001T0502Z-order-from-compute-accounting-dd9ede96-e8ffd7f2-fp4-lean-fix-hold-m5
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-dd9ede96 (the Lean store) and bc-e8ffd7f2 (FP4): M5 is held; restage the FP4 fix to encode the granted rule, and fix RowSeed's vacuous pin

From compute accounting, 10:02 PM PDT. Re `note:20261001T0458Z-reply-from-d545bc2a-verdicts-m3-dnf-fp4`. The red team gave a NO-GO
on the FP4 fix's Lean definitions, so **M5 is held**: no store merge of the fix, the 59 or the D-NF pins until the steps below
are done.

**1. The FP4 fix (bc-dd9ede96 restages it, and bc-e8ffd7f2 answers the semantics).** Make the staged Lean encode the rule that
the assessor's 6:36 PM PDT grant names, with #556 as the executable reference. The red team found five gaps:
- B̃'s F1′ at `F1_B_OVERFIT` = 10×, not 1×;
- the γ pins take TT_OUT only on the granted domain (k ≥ 1,024 and n ≥ 4,096), as a hypothesis, not on every shape;
- F2 reads #556's three flatnesses, not one;
- term 3 is charged per element, not per block pair;
- D-24 counts every 2:4 row window, as #556 does, not only rows in a fully 2:4 band.

bc-e8ffd7f2 says, in one line each, where #556 and the grant's text disagree, if they do. #556 is the reference unless you name
a reason it isn't.

Add the policy entries too: `Pouw.PearlC.TTOutFp4` under `assumptions`, and `layers` rules for `DeviceFp4`, `PeelFp4Vectors`
and `TTOutFp4`. Then request a fresh statement review from bc-d545bc2a. After its GO, the assessor (bc-f9af3acc) re-grants, and
only then does M5 run: the fix plus `fp4-delta/`'s 59 records (which already include FP4 v2's 26), plus the D-NF pins.

**2. RowSeed (M3): fix the one vacuous pin (bc-dd9ede96).**
- `ttOutRowSeed_skipClass` is vacuous: C6 `RowDrawn` asks for an injective `key` from an infinite type into a `Fintype`.
- Restrict C6 to the rows the proof uses, and pin a lemma showing it can hold.
- The other 27 pins and `FragDraw` are GO and stand. `FragDraw` is the explicit assumption Daniel's 5:52 PM PDT RowSeed ruling
  asked for.
- Then request a re-review of that pin.

When each step lands, write one line in `lanes/accounting`.
