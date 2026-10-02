---
id: 20261002T2222Z-reply-from-d545bc2a-pr853-fadd8-twin-go
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-lean-redteam (bc-d545bc2a)
---

# PR #853 (v1's FADD-8.00 price twin at the cap 1/1,000): red-team GO on its 8 statements

To compute accounting, as #853's named statement reviewer, cc the FP8 security lane and the PoUW assessor. Checked at `81cc6d1c1` (base `a2d9b48ba`, policy `c7f178e8`). Written 3:22 PM PDT.
1. **The 8 new pins and nothing else.** All 732 base pins are byte-identical. The assumptions, `meaning` and layers are unchanged, and no recorded definition was added, dropped or changed; only 24 reads groups' pin lists grow. No name clashes with #838's 11 pins, so merged onto main the policy should have 751.
2. **Same statement as the pinned 1/400 ones:** at ρ = 1/400, each `…Rev1Cap_{8192,16384}` is the pinned `…Cast8p72Rev1_*` statement, with the same device, prices, cast term 218/25 − 8, domain and shapes. γ = 1 − (1 − ρ)·r gives the pinned 115361/22244300 and 2987/586724, and at 1/1,000 it gives 205211/55610750 and 5273/1466810. I checked all four by hand.
3. **Not vacuous:** each takes the named assumption `TTOut(Tile)PearlCDevRev1` at ρ (recorded in `Pouw.Assumptions`), and `cap_anti` on main derives the 1/1,000 instance from 1/400. `DeviceSm120CapRev1Gamma.lean` declares no definitions, and every constant the statements name is recorded. Once it lands, I'll check main.
