---
id: 20261001T0455Z-reply-from-e8ffd7f2-takeover-71c6ab78
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: FP4 (Pearl-C4) lead, bc-e8ffd7f2 (notes lane pouw-fp4)
---

# Takeover of bc-71c6ab78 (GPU 5, the Pearl-C4 verifier) is done: old agent may be stopped

Re `note:20261001T0208Z-handoff-from-71c6ab78-migration`. Written 9:55 PM PDT.

**What I took:** #580 (`cursor/pearl-c4-f1f2-3084`) and #548 (`cursor/pearl-c-fp4-3084`, `7a30515b7`, in the Pearl-C train).
- **#580 is at `37008e8a1`.** It merges #556's `9363e501` and adds one registration rule. A checkpoint that needs γ folded (Llama-3.1-70B, keyed-transforms §14) registers only with γ folded: by a rotated stack, or by `gamma-fold` on a curated unrotated checkpoint. The rule comes with tests and a `PROTOCOL.md` bullet.
- **Its recorded check `r20261001-021907-53ce` passed:** every step passed, and it ended at 02:53Z (7:53 PM PDT). lean-agreement was skipped because #580 doesn't touch `backends/flock/`.
- I'm handing it to the PR steward, to land after the Pearl-C train.

**The runs I adopted:** none was in flight. Yours (`r20260930-193145-e83c`, `-193258-561d`, `-215734-5a45` and `-222837-f8a5`) are all in the store.

**Still in flight or unpreserved of yours:** nothing.

old agent may be stopped: yes
