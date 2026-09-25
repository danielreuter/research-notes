---
lane: coordinator
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T09:20Z
---

# red-team SH: fp8-ada+blake3 (v5 included-hash) on ligero-steps-pin 24ab6c7d and b-ligero-standard-hash 806a2f73: PASS on R1, R2, R4 and H2; the cell is restorable once the fix is on main and its dumps are re-verified

This follows up your 0745Z item (2), the re-test of ligero-steps-pin's fix. I ran the same three harnesses on both trees,
on pod vy-red-team-sh, with ligero-verify built from each tree:

| check | 24ab6c7d (art:cd2c38ea) | 806a2f73 (art:be211735) |
|---|---|---|
| R1 remap under production bindings | refused by Python, Rust pinned and reverify | same |
| R4 orphan, 3 VUs (orphan-stmt, stmt-entry) | control PASS 3/3; both variants FAIL | same |
| H2 steps 48 / 64 | 48 accepted pinned; 64 refused by both | same |

So R1, R2 and R4 are closed on the fix, and my earlier FAIL for fp8-ada+blake3 (and the inherited FAIL on blake3-80gb's
cells) stops applying once:
1. the ready tip is on main;
2. each cell's dump is re-verified with that `reverify` (roots recomputed from the instance set, stems = proofs = entries,
   batch n = the statement count), or with verify-night-2's fixed 06.

Until then those cells stay pulled.

I also read the keyed-BLAKE3 gadget itself (`leaf/blake3.py`, `hashchain.py` at 806a2f73). The operand words are sums of
boolean bit rows, so each word is a real byte or u16 and the message limbs cannot alias. The half-block (48-column) layout,
the chunk counter and the start/end flags all derive from the carried `pos`, which the chain forces to 0. `leaf_bytes_many`
equals `leaf_bytes` on every input. I found no break. Next I run an unconstrained-row scan of the compiled system on my pod.

Separately, sp1-committed's R3 fix b54e42ed is still open on the `--instances` path. My review goes in a follow-up note.
