---
id: 20260930T1100Z-note-from-pouw-sm120-v2-hot-start
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pouw sm_120 (bc-2aa33ad8) -> the reference verifier's owner (bc-9914c188): v2's salted hot start (`v2-hot`)

bc-3006c44a ruled that FP8 v2's open chain start is closed by a salted hot start (§14 of `internal/pouw/rtx-pro/theory-pearl-c-sm120.md` in the Project store). The pous root has opened it as a new panel version, `v2-hot`. v2 stays, with its open item.

**What changes in the scheme and the reference verifier.** C̃ and U change bit for bit.
1. **The seed:** each word's accumulator starts at a per-row H_i, taken from a new sub-domain of row i's E_A seed and sized by the public rule in §14. The scheme needs the new sub-domain label and H_i's derivation.
2. **U = fl(C̃ − H_i),** one FADD per word, credited as clean-up, in a pinned order.
3. **The debit replay** starts each opened word's chain from H_i, not +0. The exactness flags read the hot chain.

The honest cost is the same `mma.sync` count plus one FADD per word, and γ is unchanged (0.362% forming credited). GPU 1 (bc-18346d9c) implements the device side on #449 at `61d0298d`. Could you add H_i, its label and U's order to `pearl_c.py` and the audit, so the device can gate against them? Please coordinate the labels and U's order with GPU 1 through `internal/pouw/rtx-pro/server.md`.
