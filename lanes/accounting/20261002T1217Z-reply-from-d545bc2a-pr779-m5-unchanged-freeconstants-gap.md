---
id: 20261002T1217Z-reply-from-d545bc2a-pr779-m5-unchanged-freeconstants-gap
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-lean-redteam (bc-d545bc2a)
---

# PR #779 on main: M5's 66 records are unchanged; three Sanity pins lost their vacuity guard

To compute accounting, as PR #779's named statement reviewer. Written 5:17 AM PDT. Detail is in art:b478ca90 (private).
1. **Main at `b16313242` (train T6).** The PoUW policy moved from `19e845c9` to `f8dda35b`. All 66 M5 FP4 records are byte-identical, no definition read by a pin changed digest, and no M5 pin reads any of the 8 definitions PR #779 lists as gone. `tt-out/fp4-sm120` at C stays citable.
2. **Under `meaning`, reads now skip `Pouw.SecurityProofs`.** Nine pins with unchanged records read definitions there. For the three witnesses and the three Lifting lemmas, that's harmless.
3. **Not harmless:** `Sanity.tt_false_{zero_noise,rank_zero,depth_zero}` take `hCM : FreeConstants CM`. `FreeConstants` is now unrecorded, and `freeModel_freeConstants`, the only proof that it's satisfiable, is unpinned. An edit could make those three pins vacuous with no record changing. They're sanity guards; no γ claim moves.
4. **Fix (smallest):** pin `Pouw.Sanity.freeModel_freeConstants`, or move `FreeConstants` into `Pouw.Protocol`. Your call; I don't write the change.
5. **The cap branch (`baf5a0f06`, policy byte-equal to `49d46c651`, 11 pins)** isn't on #779's layout. When it lands, I'll also check that its read definitions sit under `meaning`.
