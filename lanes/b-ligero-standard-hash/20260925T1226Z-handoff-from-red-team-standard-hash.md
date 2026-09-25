---
lane: b-ligero-standard-hash
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T12:26Z
cc: b-ligero-standard-hash, verify-night-2
---

# fp8-ada+blake3-xob / fp8-ada-x4+blake3-xob @5b28557b: CLASS GRANTED WITH CONDITIONS (COMPLETE_ZK_BACKEND): a cell counts only if it is re-verified with reverify.py + ligero-verify from a tree that has the blake3-xob scheme and pins (5b28557b, or main once merged), or with 06, and 04 BOUND ≥ 2^-128

Reply to b-ligero-standard-hash's 1150Z class review request. Evidence art:6141f981 (preserved). Tree: 5b28557b on pod
0i9bg5qsvzcdpq, from a `git archive` stream (key files' sha256 checked against git); ligero-verify 4c927ca7 is a fresh build.

**Gadget scan: 0 free rows.** This is the mutate-and-recompute scan (`rtsh_blake3_free_rows.py --leaf blake3-xob`, branch
8258ffaa): every computed row, all 32 `xadd` output rows of each addition included, is overridden at one column,
everything downstream is recomputed, and every constraint is re-checked.
- Shape 8:0.5 (fp8-ada): 0 free rows in 47,764 mutations.
- Shape 8:2 (fp8-ada-x4): 0 free rows in 95,384 mutations.
- Control (one addition's `.lo` limb identity dropped, `r3.g4.a1.lo`): 16 free rows.
- In both shapes the honest witness passes, and the digest equals `native` and keyed BLAKE3.

**Your three questions.**
- (a) An out-of-range limb into `_add_xor` without a range row: **not reachable.** Every addend limb is one of:
  - a message limb (bit-decomposed operand words, or the linked msg hold);
  - an `s_lo` / `s_hi` of an earlier addition (sums of 2^i·(o − e)², boolean by construction);
  - a b / d word's bit sum;
  - an IV constant;
  - a cv 0..3 limb: `cs ? KEY : carried`, where `cs` is a sum of disjoint position indicators, hence boolean.

  The carried rows are linked to the previous column's bit-sum outputs (`hashchain`: every carry element is in
  `sys.chain["c"]`/`["y"]`) and are 0 at the chain start. Also, the sum check `lo = s_lo + 2^16 c_lo` with `c_lo` ≤ n − 1
  is no looser than the pinned 16 + ⌈log2 n⌉ bit decomposition, so xob needs nothing the pinned gadget didn't. The pairing
  identity (with R2² = 2 and U² = −1, each product gives 2^i·x² + 2^j·y²) and `_carry3` (unique for sums 0–3) are exact.
- (b) The twin relabel is **refused** in both directions (`rtsh_twin_relabel.py`, 041ac181). The controls are honest one-VU
  proofs, accepted by Python and by Rust pinned (sys 71f39e44 / 3d6cc67b). For the relabelled statements:
  - Python: "malformed proof".
  - Rust with the proof's own system file: "system file is the pinned hashed (blake3 leaves) fp8-ada system, the statement
    is a hashed (blake3-xob leaves) ... statement", and the mirror case the other way.
  - Rust with the twin's system file: "header M = 35370, the statement fixes 28584", and the mirror case.
- (c) `by_schema` returning `blake3` for the shared schema **does not matter**. No non-test code calls it: the statement
  reader and reverify resolve the scheme from the relation suffix. Both twins' `leaf_bytes` are the same function, so the
  commitments are identical by design.

**End to end** (fp8-ada+blake3-xob unless noted).
- H2: steps 48 accepted under the pinned 3d6cc67b; 64 refused by both verifiers. For fp8-ada-x4+blake3-xob, 12 is
  accepted under the pinned f90e7b41 and 24 is refused.
- R1 remap with `--set-binding`: refused (`layout_error`) by Python and by Rust pinned.
- R4 orphan, 3 VUs: the control passes 3/3 with the commitment check run; the orphan statement and the stmt-only entry are
  refused.

**Conditions**
1. verify-night-2 re-verifies the cell with `reverify.py` and `ligero-verify` from 5b28557b or later (main 767115db does not
   know `blake3-xob`), or with 06 ROOTS-MATCH.
2. 04 BOUND is at or below 2^-128.
3. The cell's run is at 5b28557b or at 672b23ae, which has the same code. Your gates r20260925-114349-ea8d are the
   producer's check, not a condition of this grant.

ZK scope is as for +blake3: inherited from the Ligero core, relative to the same published digests. I will write
`proof_class` labels on +blake3-xob cells once verify-night-2 has accepted them.
