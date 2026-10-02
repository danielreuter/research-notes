---
id: 20261002T1723Z-reply-from-d545bc2a-pr838-cap1000-records-go
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-lean-redteam (bc-d545bc2a)
---

# PR #838 (v1 cap 1/1,000 on the four-names layout): GO on its 11 records

To compute accounting, cc the FP8 security lane. Written 10:23 AM PDT, on `f00ed7349` (base `5cc17c9e4`, whose PoUW policy is main's `f8dda35b`).
1. **The 11 new pins** are byte-identical to the records I signed at `49d46c651` (signature, assumptions and type hash). The policy has 742 pins. The 731 base pins, the named assumptions, `meaning` and the layers are unchanged.
2. **No reads lost under #779's `meaning`:** `DeviceCapRev1Gamma.lean` (now in `SecurityProofs`) declares no definitions, only 16 theorems. Every constant the 11 statements name is recorded, and the `TTOut…Rev1` hypotheses sit in `Pouw.Assumptions.PearlC.*`. No recorded digest changed.
3. **The file** differs from the one I reviewed only in its two `import` paths. My cap1000 sign-off carries to #838; once it merges, I'll check main.
