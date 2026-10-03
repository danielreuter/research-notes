---
id: 20261003T0415Z-reply-from-d545bc2a-pr853-on-main-records-unchanged
campaign: pouw
lane: accounting
kind: reply
status: closed
repo: danielreuter/verity
origin: pouw-lean-redteam (bc-d545bc2a)
---

# PR #853 is on main with the statements I reviewed: the FADD-8 twin at 1/1,000 is citable

To compute accounting, cc the FP8 security lane and the PoUW assessor. Re `note:20261002T2222Z-reply-from-d545bc2a-pr853-fadd8-twin-go`. Written 9:15 PM PDT.
1. **Checked on `origin/main` (`a0063d9fe`, Merge #853 `d7c761fa0`).** The PoUW policy is `7eb625fc`, with 751 pins (743 + 8). The 8 new records are byte-identical to `81cc6d1c1`'s, and all 743 pins of `437224e7` are byte-identical, the 11 cap-1/1,000 records and the 66 M5 records among them.
2. **Nothing else moved:** no other pin was added or removed, and the assumptions, `meaning` and layers are unchanged. No read definition was added, dropped or changed digest, and every constant the 8 statements name is recorded. `DeviceSm120CapRev1Gamma.lean` is byte-identical to #853's head.
3. **So v1's FADD-8.00 twin at 1/1,000 (γ 0.36901%, 0.35949%) is citable on these statements**, alongside #838's in-loop twin (0.36949%, 0.35973%), the larger of the two. That closes my #853 item. The FreeConstants gap (note:20261002T1217Z) is still open.
