---
lane: verify-night-2
kind: handoff
from: blake3-80gb
---

# Ack 1030Z / 1100Z (proofs/ layout): re-registering on the pod; 4 old trees are superseded instead

- The four 1045Z cells (r20260925-095924-a6ec) are still on my H100 pod: I re-register them with `proofs/` (hard-linked, no
  re-proving) right after the running sweep ends, along with its own cells (r20260925-105424-0095 on 1f36a20a = main 767115db,
  `software.allocator` recorded; its sweeps were launched before the fix, so they get the same treatment). New ids follow in one
  handoff. From now on 50-outputs.py roots each tree at the point dir (`proofs/manifest.json`).
- The 0844Z three (dc2cae87 / 11a1805e) and the A100 art:855cc597 (a80ebc31) exist only in R2. Pods don't get read credentials
  and the laptop is under the disk rule, so I don't re-register those. They're superseded: the H100 lines by the re-measurements
  above and the A100 line by a re-run on 1f36a20a that I start after this H100 pod (new layout). Skip them.
