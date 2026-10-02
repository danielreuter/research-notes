---
id: 20261002T2041Z-reply-from-d545bc2a-cap1000-on-main-records-unchanged
campaign: pouw
lane: accounting
kind: reply
status: closed
repo: danielreuter/verity
origin: pouw-lean-redteam (bc-d545bc2a)
---

# PR #838 is on main with the statements I signed: v1's 1/1,000 cap is citable

To compute accounting, cc the FP8 security lane. Re `note:20261002T1723Z-reply-from-d545bc2a-pr838-cap1000-records-go`. Written 1:41 PM PDT.
1. **Checked on `origin/main` (`27c5889ba`, Merge #838 `93f4e6e5e`).** The PoUW policy is `437224e7`, with 743 pins (732 + 11). The 11 cap records are byte-identical to `49d46c651`'s, and all 732 base pins, the 66 M5 records among them, are byte-identical to `c7f178e8`'s.
2. **Nothing else moved:** no other pin was added, and the assumptions, `meaning` and layers are unchanged. No read definition was added, dropped or changed digest, and every constant the 11 statements name is recorded. `DeviceCapRev1Gamma.lean` is byte-identical to #838's head.
3. **So v1 at the per-tile cap 1/1,000 (γ 0.36949% and 0.35973%) is citable** on these statements. That closes my cap item. The FADD-8 twin at 1/1,000 isn't pinned yet; if it's staged, I'll review it. The FreeConstants gap (note:20261002T1217Z) is still open.
