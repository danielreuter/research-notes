---
lane: poseidon-v1
kind: handoff
from: verify-night-2
created: 2026-09-25T11:00Z
---

# 5090 NVFP4 art:70f275ac / art:6740eb22: not re-verifiable yet (fail-closed). Main's reverify has no fp4-nvf4 relation

I stopped at art:70f275ac, run r20260925-103509-76d9, main 3301c435. The failing path is in main's reverify:
- `committed_trees` (the R2 recompute) calls `relations.relation('fp4-nvf4')`.
- That raises "unknown --relation 'fp4-nvf4'", because `backends/direct/ligero/relations.py` registers only the fp8 and bf16
  families. fp4 lives in `fp4/chain.py`.

relations.py and reverify.py are unchanged in main 767115db, so the refusal stands there too. Since reverify never passes, no
label was written. I also stopped the plateau before its reverify, because it would fail the same way.

My own checks on art:70f275ac all pass (tree d8a0d856):
- 04 BOUND against fp4-nvf4 over [0, 4096).
- 06 ROOTS-MATCH: a 84ce9030, b 3f2303f6, y 68c80a14.
- The 05 negatives with ligero-verify 596529d2: base ACCEPT 13/13 at 2^-128.11; proofbyte, stmtbyte and swapstmt REJECT.

Getting the cell to count needs a main change: reverify's `committed_trees` has to know fp4-nvf4. That's a coordinator
decision, and I've told the coordinator.
