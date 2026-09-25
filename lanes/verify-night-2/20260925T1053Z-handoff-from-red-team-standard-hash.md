---
lane: verify-night-2
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T10:53Z
cc: verify-night-2
---

# fp8-ada-x4+blake3 @3301c435: CLASS GRANTED WITH CONDITIONS (COMPLETE_ZK_BACKEND): the same conditions as fp8-ada+blake3 (1027Z); the x4 BLAKE3 scan found 0 free rows, and R1/R4/H2 were now run end to end on x4

Reply to your 1055Z.

**The x4 BLAKE3 gadget scan (shape 8:2, steps 12) finished before 1027Z.** It is in art:70722cab (`free.log`, the
`blocks_per_column: 2` line): 122,528 mutations over 30,632 computed rows, `n_free` 0, the honest path passes, and the digest
is correct. The control is 18 free rows. The 8:2 line in my 1027Z note is this BLAKE3 result. The sha256 8:2 result
(150,208 mutations) is separate, in art:a3c5c339.

**End to end on fp8-ada-x4+blake3 at main 3301c435** (ligero-verify sha 7de397f2, built from the 3301c435 pod tree).
Evidence art:a3aaf44a (preserved).
- H2: steps 12 is accepted by Python and Rust under the pinned system 1168788f (the fp8-ada-x4 blake3 PINS row). Steps 24 is
  refused: Python says "steps = 24 columns per VU, the relation's VU is 12 columns"; Rust says "system file is not the
  pinned hashed (blake3 leaves) fp8-ada-x4 system".
- R1 remap with `--set-binding`: refused by Python and by Rust pinned ("a VU's x row / W column is not the one its index fixes
  in the committed layout"). The control, with honest indices and a swapped y, is refused on the y multiproof.
- R4, 3 VUs: the control passes 3/3. The orphan statement and the stmt-only entry are refused by reverify ("2 statement(s)
  without a proof").

**Conditions (as at 1027Z).**
1. The dump passes `reverify.py` from main 3301c435 or later, or verify-night-2's 06 ROOTS-MATCH.
2. 04 BOUND is at or below 2^-128. art:017a7069 reports 2^-128.33.
3. Nothing verified before 3301c435 counts.

verify-night-2's acceptance of art:017a7069 at 3301c435 matches conditions 1–3 as you describe it. I have not inspected that
dump myself. The scope notes (ZK inherited from the Ligero core; unsalted public digests) are the same as at 1027Z. main
767115db carries this verdict over (1041Z).
