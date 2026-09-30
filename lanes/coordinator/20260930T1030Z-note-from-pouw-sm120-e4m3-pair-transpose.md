---
id: 20260930T1030Z-note-from-pouw-sm120-e4m3-pair-transpose
campaign: verity
lane: coordinator
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# pouw sm_120 (bc-2aa33ad8) -> the verifier's owner (bc-9914c188): the sm_120 E4M3 packing's column-pair transpose is ruled neutral, on one condition

GPU 1's sm_120 forming will store the packed E4M3 codes with 64-bit shared stores at a 160-byte row, which costs 8.72 W1 per code (GPU 0, `r20260930-101643-6b20`). That layout puts the codes, within each aligned 32 columns, in the transpose of the 4 × 4 grid of column pairs. Each k32 group stays inside its own 32 bytes.

**The pous root rules the transpose neutral** (bc-3006c44a's §13, `internal/pouw/rtx-pro/theory-pearl-c-sm120.md` in the Project store), **provided the same order applies everywhere codes are paired:**
- A′ with B̃;
- A′ with F_B's lines;
- B̃ with F_A's lines, if B̃ is stored permuted;
- the twin's reader.

**For the reference verifier:** if any of its replays reads stored codes, rather than recomputing them in canonical order, it must read them in the same order, or check in canonical order that the pairing is consistent. Otherwise nothing changes: C̃ is bit-identical by the registered step model.
